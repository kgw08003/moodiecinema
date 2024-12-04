import requests

API_KEY = '5f0eb3027f1b131897e4dcbe057e0931'
BASE_URL = 'https://api.themoviedb.org/3/movie/'


def fetch_data_from_api(endpoint, params=None):
    """
    공통 API 호출 함수
    :param endpoint: API 엔드포인트 URL
    :param params: 추가 파라미터
    :return: JSON 데이터
    """
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request Exception: {e}")
        return None


def get_movie_data(movie_id):
    """
    영화 기본 정보를 가져오는 함수
    """
    # API에서 데이터 가져오기
    data = fetch_data_from_api(f'{BASE_URL}{movie_id}', {'language': 'ko-KR'})
    if data:
        # id 필드 추가 (필요 시)
        if 'id' not in data:
            data['id'] = movie_id
        return data
    return None



def get_movie_credits(movie_id):
    """
    영화 출연진 및 제작진 정보를 가져오는 함수
    """
    credits = fetch_data_from_api(f'{BASE_URL}{movie_id}/credits', {'language': 'ko-KR'})
    if not credits:
        return None

    cast = credits.get('cast', [])
    crew = credits.get('crew', [])
    for actor in cast:
        actor['profile_image_url'] = f"https://image.tmdb.org/t/p/w200{actor['profile_path']}" if actor.get('profile_path') else '/static/images/default-profile.png'

    director = next((member for member in crew if member['job'] == 'Director'), None)
    if director:
        director['profile_image_url'] = f"https://image.tmdb.org/t/p/w200{director['profile_path']}" if director.get('profile_path') else '/static/images/default-profile.png'

    return {'cast': cast, 'director': director}


def get_movie_videos(movie_id):
    """
    영화 관련 동영상을 가져오는 함수
    """
    return fetch_data_from_api(f'{BASE_URL}{movie_id}/videos', {'language': 'ko-KR'})


def get_similar_movies(genre_ids, exclude_movie_id=None):
    all_movies = fetch_data_from_api(
        "https://api.themoviedb.org/3/discover/movie",
        {'with_genres': ','.join(map(str, genre_ids)), 'language': 'ko-KR'}
    ).get("results", [])
    
    if exclude_movie_id is not None:
        all_movies = [movie for movie in all_movies if movie.get("id") != exclude_movie_id]
    
    return all_movies[:8]



def get_tmdb_reviews(movie_id, sort_option='newest'):
    """
    TMDb 리뷰를 가져오는 함수
    """
    reviews = fetch_data_from_api(f'{BASE_URL}{movie_id}/reviews', {'language': 'en-US'}).get('results', [])
    if sort_option == 'highest_rating':
        return sorted(reviews, key=lambda x: x['author_details'].get('rating', 0), reverse=True)
    elif sort_option == 'lowest_rating':
        return sorted(reviews, key=lambda x: x['author_details'].get('rating', 0))
    return sorted(reviews, key=lambda x: x['created_at'], reverse=True)
