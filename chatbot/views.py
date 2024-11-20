from django.http import JsonResponse
from django.views import View
import requests, random
from django.conf import settings

class ChatbotAPIView(View):
    def post(self, request):
        import json
        try:
            data = json.loads(request.body)
            print(f"사용자 입력: {data}")  # 디버깅용 로그
            user_message = data.get('message', '').lower()

            # 장르 키워드 매핑
            genre_keywords = {
                '액션': 'Action',
                '드라마': 'Drama',
                '코미디': 'Comedy',
                '모험': 'Adventure',
                '애니메이션': 'Animation',
                '범죄': 'Crime',
                '다큐멘터리': 'Documentary',
                '가족': 'Family',
                '판타지': 'Fantasy',
                '역사': 'History',
                '공포': 'Horror',
                '음악': 'Music',
                '미스터리': 'Mystery',
                '로맨스': 'Romance',
                'SF': 'Science Fiction',
                'TV': 'TV Movie',
                '스릴러': 'Thriller',
                '전쟁': 'War',
                '서부': 'Western'
            }

            genre = None
            for keyword, genre_name in genre_keywords.items():
                if keyword in user_message:
                    genre = genre_name
                    break

            # 장르에 따른 영화 추천
            if genre:
                response = self.get_movie_recommendations(genre=genre)
            elif '추천' in user_message:
                response = self.get_movie_recommendations()
            else:
                response = "영화를 추천받고 싶다면 '추천', '액션 영화', '코미디 영화', '공포 영화' 등으로 요청해주세요!"

            return JsonResponse({'response': response})
        except Exception as e:
            print(f"에러 발생: {e}")  # 에러 상세 출력
            return JsonResponse({'response': f'서버에서 오류가 발생했습니다. 상세: {e}'}, status=500)

    def get_movie_recommendations(self, genre=None):
        api_key = settings.TMDB_API_KEY
        if not api_key:
            print("API 키가 설정되지 않았습니다.")
            return "서버 설정 오류로 인해 영화를 추천할 수 없습니다."

        url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
            "language": "ko-KR",
        }

        # 장르 매핑
        genre_mapping = {
            'Action': 28,
            'Drama': 18,
            'Comedy': 35,
            'Adventure': 12,
            'Animation': 16,
            'Crime': 80,
            'Documentary': 99,
            'Family': 10751,
            'Fantasy': 14,
            'History': 36,
            'Horror': 27,
            'Music': 10402,
            'Mystery': 9648,
            'Romance': 10749,
            'Science Fiction': 878,
            'TV Movie': 10770,
            'Thriller': 53,
            'War': 10752,
            'Western': 37
        }

        # 장르 필터 적용
        if genre:
            genre_id = genre_mapping.get(genre.capitalize())
            if genre_id:
                params["with_genres"] = genre_id
                print(f"장르 필터 적용: {genre} (ID: {genre_id})")
            else:
                return f"'{genre}' 장르를 찾을 수 없습니다. 다른 장르를 시도해보세요!"

        # TMDb API 호출
        try:
            all_movies = []  # 최대 100개 영화를 저장할 리스트
            for page in range(1, 6):  # 최대 5페이지 데이터 가져오기 (1페이지에 20개)
                params["page"] = page
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    movies = data.get('results', [])
                    all_movies.extend(movies)
                else:
                    print(f"페이지 {page} 호출 실패")
                    break

            # 랜덤으로 5개의 영화 선택
            if all_movies:
                selected_movies = random.sample(all_movies, min(5, len(all_movies)))
                return "\n".join([f"{movie['title']} ({movie.get('release_date', '개봉일 미정')})" for movie in selected_movies])
            else:
                return "추천할 영화가 없습니다. 다른 장르를 시도해보세요!"
        except Exception as e:
            print(f"API 요청 중 오류 발생: {e}")
            return f"API 요청 중 오류가 발생했습니다: {e}"
