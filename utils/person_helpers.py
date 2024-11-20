import requests

API_KEY = '5f0eb3027f1b131897e4dcbe057e0931'
BASE_URL = 'https://api.themoviedb.org/3/person/'


def fetch_person_data(person_id):
    """
    특정 배우/감독의 기본 정보를 가져오는 함수
    """
    try:
        response = requests.get(
            f'{BASE_URL}{person_id}',
            params={'api_key': API_KEY, 'language': 'ko-KR'}
        )
        response.raise_for_status()
        person = response.json()
        person['profile_image_url'] = (
            f"https://image.tmdb.org/t/p/w300{person['profile_path']}"
            if person.get('profile_path')
            else '/static/images/default-profile.png'
        )
        return person
    except requests.exceptions.RequestException as e:
        print(f"Error fetching person data: {e}")
        return None


def fetch_movie_credits(person_id):
    """
    특정 배우/감독의 출연 영화 또는 제작 영화 정보를 가져오는 함수
    """
    try:
        response = requests.get(
            f'{BASE_URL}{person_id}/movie_credits',
            params={'api_key': API_KEY, 'language': 'ko-KR'}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie credits: {e}")
        return None


def get_cast_movies(person_id):
    """
    특정 배우의 출연 영화를 가져오는 함수
    """
    credits = fetch_movie_credits(person_id)
    if not credits:
        return []
    return sorted(
        credits.get('cast', []),
        key=lambda x: x.get('release_date', ''),
        reverse=True
    )


def get_director_movies(person_id):
    """
    특정 감독의 제작 영화를 가져오는 함수
    """
    credits = fetch_movie_credits(person_id)
    if not credits:
        return []
    return sorted(
        [movie for movie in credits.get('crew', []) if movie['job'] == 'Director'],
        key=lambda x: x.get('release_date', ''),
        reverse=True
    )
