from django.views.generic import TemplateView
import requests
from django.shortcuts import render

class MovieDetailView(TemplateView):
    template_name = 'moodiecine/movies.html'
    
    # API 키 및 기본 URL
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'  # 실제 API 키로 교체하세요
    base_url = 'https://api.themoviedb.org/3/movie/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs['movie_id']

        # 영화 정보 가져오기
        movie_response = requests.get(f'{self.base_url}{movie_id}?api_key={self.api_key}&language=ko-KR')
        credits_response = requests.get(f'{self.base_url}{movie_id}/credits?api_key={self.api_key}&language=ko-KR')
        videos_response = requests.get(f'{self.base_url}{movie_id}/videos?api_key={self.api_key}&language=ko-KR')

        # 에러 처리
        if movie_response.status_code != 200 or credits_response.status_code != 200:
            context['error'] = '영화 정보를 가져오는 데 실패했습니다.'
            return context

        # JSON 응답을 파싱
        movie_data = movie_response.json()
        credits_data = credits_response.json()
        videos_data = videos_response.json()

        # 컨텍스트에 데이터 추가
        context['movie'] = movie_data
        context['cast'] = credits_data['cast'][:5]  # 상위 5명 출연진

        # 유사한 영화 가져오기
        genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
        similar_movies = self.get_similar_movies_from_tmdb(genre_ids)
        context['similar_movies'] = similar_movies[:8]
        
        youtube_videos = [video for video in videos_data['results'] if video['site'] == 'YouTube']
        if youtube_videos:
            context['youtube_trailers'] = youtube_videos[:2]  # 상위 2개 예고편 가져오기
        else:
            context['youtube_trailers'] = None  # 예고편이 없으면 None 설정
            
        
        return context
        

    def get_similar_movies_from_tmdb(self, genre_ids):
        response = requests.get("https://api.themoviedb.org/3/discover/movie", params={
            "api_key": self.api_key,
            "with_genres": ",".join(map(str, genre_ids))
        })
        return response.json().get("results", [])
