import requests
from django.conf import settings
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MovieChatbotHTMLView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'moodiecinema/chatbot.html')  # HTML 템플릿 경로


class MovieChatbotView(APIView):
    def __init__(self):
        self.user_state = {}  # 사용자 상태 관리

    def get(self, request, *args, **kwargs):
        # 쿼리 파라미터에서 user_id와 user_message를 가져옴
        user_id = request.query_params.get('user_id', None)
        user_message = request.query_params.get('user_message', None)

        # user_id와 user_message가 없으면 400 Bad Request 반환
        if not user_id or not user_message:
            return Response({"message": "user_id와 user_message 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Received message from {user_id}: {user_message}")  # 디버깅용 로그

        # 사용자 상태가 없으면 'start'로 초기화
        if user_id not in self.user_state:
            self.user_state[user_id] = 'start'

        # 영화 추천 요청 처리
        if user_message and self.user_state[user_id] == 'start' and '영화 추천' in user_message:
            self.user_state[user_id] = 'waiting_for_genre'
            genres = self.get_genres()  # 동적으로 장르 목록 가져오기
            return Response({
                "message": "어떤 장르를 선호하시나요? (예: 액션, 드라마, 코미디 등)",
                "genres": genres
            }, status=status.HTTP_200_OK)

        # 장르에 대한 응답 처리
        if self.user_state.get(user_id) == 'waiting_for_genre':
            genre = user_message.strip().lower()  # 공백 제거하고 소문자로 처리
            genre_id = self.get_genre_id(genre)

            # 장르 매칭 실패 시 오류 반환
            if genre_id is None:
                print(f"Invalid genre input: {genre}")  # 디버깅용 로그
                return Response({"message": "지원하지 않는 장르입니다. 다른 장르를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

            recommended_movies = self.get_movie_recommendations_by_genre(genre_id)  # 장르에 맞는 영화 추천
            self.user_state[user_id] = 'waiting_for_movie'

            return Response({
                "message": f"{genre} 장르의 영화들을 추천합니다.",
                "movies": recommended_movies
            }, status=status.HTTP_200_OK)

        # 영화에 대한 응답 처리
        if self.user_state.get(user_id) == 'waiting_for_movie':
            movie_name = user_message
            movie_info = self.get_movie_info(movie_name)

            if movie_info:
                self.user_state[user_id] = 'waiting_for_more_info'
                return Response({
                    "message": f"{movie_name}의 줄거리는 다음과 같습니다: {movie_info['overview']}",
                    "more_info": "더 궁금한 정보가 있으면 말씀해 주세요."
                }, status=status.HTTP_200_OK)

        return Response({"message": "저는 영화 관련 정보만 제공해 드릴 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)
    def get_genre_id(self, genre_name):
        genre_name = genre_name.strip().lower()  # 소문자와 공백 처리
        print(f"Received genre name (after strip and lower): '{genre_name}'")  # 장르 이름 출력
        genres = {
            '액션': 28,
            '드라마': 18,
            '코미디': 35,
            '모험': 12,
            '애니메이션': 16,
            '범죄': 80,
            '다큐멘터리': 99,
            '가족': 10751,
            '판타지': 14,
            '역사': 36,
            '공포': 27,
            '음악': 10402,
            '미스터리': 9648,
            '로맨스': 10749,
            'sf': 878,  # 'SF'는 소문자로 변경됨
            'tv 영화': 10770,
            '스릴러': 53,
            '전쟁': 10752,
            '서부': 37,  # 서부 장르 추가
        }
        print(f"Genres available: {list(genres.keys())}")  # 사용 가능한 장르 확인
        genre_id = genres.get(genre_name)  # 해당 장르의 ID를 가져옵니다
        if genre_id is None:
            print(f"Genre '{genre_name}' not found in genres list.")
        else:
            print(f"Genre ID for '{genre_name}': {genre_id}")
        return genre_id


    def get_movie_recommendations_by_genre(self, genre):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre}&language=ko'
        try:
            response = requests.get(url)
            data = response.json()
            recommended_movies = [movie['title'] for movie in data['results'][:5]]
            if len(recommended_movies) < 5:
                # 5개 미만일 경우 최대한 다 추천
                recommended_movies = [movie['title'] for movie in data['results']]
            return recommended_movies
        except requests.exceptions.RequestException as e:
            return {"error": "영화 추천을 가져오는 데 실패했습니다."}

    def get_movie_info(self, movie_name):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}&language=ko'
        try:
            response = requests.get(url)
            data = response.json()
            if data['results']:
                movie = data['results'][0]
                movie_details = {
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'release_date': movie['release_date'],
                    'rating': movie['vote_average'],
                    'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else "https://via.placeholder.com/500x750?text=No+Image",
                    'cast': self.get_movie_cast(movie['id']),
                    'director': self.get_movie_director(movie['id']),
                    'similar_movies': self.get_similar_movies(movie['id']),
                    'trailer': self.get_movie_trailer(movie['id']),
                }
                return movie_details
        except requests.exceptions.RequestException as e:
            return {"error": "영화 정보를 가져오는 데 실패했습니다. 다시 시도해주세요."}
        return None

    def get_genres(self):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=ko'
        try:
            response = requests.get(url)
            data = response.json()
            genres = {genre['name'].lower(): genre['id'] for genre in data['genres']}  # 소문자로 변환하여 저장
            return genres
        except requests.exceptions.RequestException as e:
            return {"error": "장르 목록을 가져오는 데 실패했습니다."}

    def get_movie_cast(self, movie_id):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=ko'
        response = requests.get(url)
        data = response.json()
        cast = [actor['name'] for actor in data['cast'][:5]]
        return cast

    def get_movie_director(self, movie_id):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=ko'
        response = requests.get(url)
        data = response.json()
        director = next((crew['name'] for crew in data['crew'] if crew['job'] == 'Director'), '정보 없음')
        return director

    def get_similar_movies(self, movie_id):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={api_key}&language=ko'
        response = requests.get(url)
        data = response.json()
        similar_movies = [movie['title'] for movie in data['results'][:5]]
        return similar_movies

    def get_movie_trailer(self, movie_id):
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=ko'
        response = requests.get(url)
        data = response.json()
        if data['results']:
            trailer = data['results'][0]['key']
            return f"https://www.youtube.com/watch?v={trailer}"
        return "트레일러 정보 없음"
