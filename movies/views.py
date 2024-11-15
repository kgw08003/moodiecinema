#movies/views.py
from django.views.generic import TemplateView
import requests
from django.shortcuts import render
from reviews.views import ReviewListView, ReviewCreateView  # 리뷰 관련 뷰 추가
from .models import Movies


class MovieDetailView(TemplateView):
    template_name = 'moodiecinema/movies.html'
    
    # API 키 및 기본 URL
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'  # 실제 API 키로 교체하세요
    base_url = 'https://api.themoviedb.org/3/movie/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs['movie_id']

        # 영화 정보 가져오기
        movie_response = requests.get(f'{self.base_url}{movie_id}?api_key={self.api_key}&language=ko-KR')
        movie_data = movie_response.json()
        credits_response = requests.get(f'{self.base_url}{movie_id}/credits?api_key={self.api_key}&language=ko-KR')
        videos_response = requests.get(f'{self.base_url}{movie_id}/videos?api_key={self.api_key}&language=ko-KR')


        # 에러 처리
        if movie_response.status_code != 200 or credits_response.status_code != 200:
            context['error'] = '영화 정보를 가져오는 데 실패했습니다.'
            return context

        # JSON 응답을 파싱
        credits_data = credits_response.json()
        videos_data = videos_response.json()

        # 영화 객체를 DB에서 가져오거나 새로 생성 및 업데이트
        movie, created = Movies.objects.get_or_create(
            movie_id=movie_id,
            defaults={
                'user': self.request.user,
                'content': movie_data.get('overview', ''),
                'poster_path': movie_data.get('poster_path', ''),
                'title': movie_data.get('title', '')  # 제목 저장
            }
        )

        # 객체가 이미 존재할 경우 title과 poster_path가 업데이트되도록 보장
        if not created:
            updated = False
            if movie.poster_path != movie_data.get('poster_path', ''):
                movie.poster_path = movie_data.get('poster_path', '')
                updated = True
            if movie.title != movie_data.get('title', ''):
                movie.title = movie_data.get('title', '')
                updated = True
            if updated:
                movie.save()  # 변경 사항이 있을 때만 저장

        # 컨텍스트에 데이터 추가
        context['movie'] = movie_data
        context['cast'] = credits_data['cast'][:5]  # 상위 5명 출연진
        context['movie_id'] = movie_id  # movie_id를 템플릿에 전달
        
        # 유사한 영화 가져오기
        genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
        similar_movies = self.get_similar_movies_from_tmdb(genre_ids)
        context['similar_movies'] = similar_movies[:8]
        
        youtube_videos = [video for video in videos_data['results'] if video['site'] == 'YouTube']
        if youtube_videos:
            context['youtube_trailers'] = youtube_videos[:2]  # 상위 2개 예고편 가져오기
        else:
            context['youtube_trailers'] = None  # 예고편이 없으면 None 설정

        # 리뷰 가져오기
        #tmdb_reviews_response = requests.get(f'{self.base_url}{movie_id}/reviews?api_key={self.api_key}&language=ko-KR')

        # TMDb 영어 리뷰 가져오기
        tmdb_reviews_response = requests.get(f'{self.base_url}{movie_id}/reviews?api_key={self.api_key}&language=en-US')
        if tmdb_reviews_response.status_code == 200:
            tmdb_reviews_data = tmdb_reviews_response.json()
            context['tmdb_reviews'] = tmdb_reviews_data.get('results', [])
        else:
            context['tmdb_reviews'] = []  # 리뷰 데이터가 없을 때 빈 리스트 설정

        # 사용자 리뷰 가져오기

        ####### 리뷰 리스트 추가 #######
        review_list_view = ReviewListView()
        review_list_view.kwargs = {'movie_id': movie_id}
        context['reviews'] = review_list_view.get_queryset()
        context['review_form'] = ReviewCreateView.form_class()
    
        return context
        

    def get_similar_movies_from_tmdb(self, genre_ids):
        response = requests.get("https://api.themoviedb.org/3/discover/movie", params={
            "api_key": self.api_key,
            "with_genres": ",".join(map(str, genre_ids))
        })
        return response.json().get("results", [])
    
    
    