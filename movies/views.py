from django.views.generic import TemplateView
from django.shortcuts import render
import json
from reviews.views import ReviewCreateView
from utils.movie_helpers import (
    get_movie_data,
    get_movie_credits,
    get_movie_videos,
    get_similar_movies,
    get_tmdb_reviews
)
from utils.review_helpers import get_reviews_with_list_view, analyze_reviews

EMOJI_MAPPING = {
    "슬픔": "😢",
    "공포": "😨",
    "분노": "😡",
    "평온": "😌",
    "기쁨": "😊",
    "감정 없음": "❔"
}

class MovieDetailView(TemplateView):
    template_name = 'moodiecinema/movies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs['movie_id']

        # API 데이터 가져오기
        movie_data = get_movie_data(movie_id)
        if not movie_data:
            context['error'] = '영화 정보를 가져오는 데 실패했습니다.'
            return context

        credits_data = get_movie_credits(movie_id)
        videos_data = get_movie_videos(movie_id)

        # 영화 관련 데이터 추가
        context['movie'] = movie_data
        context['cast'] = credits_data.get('cast', []) if credits_data else []
        context['director'] = credits_data.get('director')

        # 비슷한 영화 가져오기
        genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
        context['similar_movies'] = get_similar_movies(genre_ids)

        # 유튜브 트레일러 추가
        youtube_videos = [
            video for video in videos_data.get('results', []) if video['site'] == 'YouTube'
        ]
        context['youtube_trailers'] = youtube_videos[:2] if youtube_videos else None

        # TMDb 리뷰 가져오기
        sort_option = self.request.GET.get('sort_tmdb', 'newest')
        context['tmdb_reviews'] = get_tmdb_reviews(movie_id, sort_option)

        # 사용자 리뷰 가져오기 및 분석
        reviews = get_reviews_with_list_view(self.request, movie_id)
        review_analysis = analyze_reviews(reviews)
        context.update(review_analysis)

        # 추가 데이터
        context['total_sentiment_emoji'] = EMOJI_MAPPING.get(review_analysis['total_sentiment'], "❔")
        context['reviews'] = reviews
        context['review_form'] = ReviewCreateView.form_class()

        return context

from utils.person_helpers import fetch_person_data, get_cast_movies,fetch_person_data, get_director_movies

class ActorMoviesView(TemplateView):
    template_name = 'moodiecinema/actor_movies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_id = self.kwargs['person_id']

        # 배우 정보 가져오기
        person_data = fetch_person_data(person_id)
        if person_data:
            context['person'] = person_data
        else:
            context['error'] = '해당 배우 정보를 가져오는 데 실패했습니다.'

        # 배우의 출연 영화 가져오기
        context['cast_movies'] = get_cast_movies(person_id)[:20]

        return context

class DirectorMoviesView(TemplateView):
    template_name = 'moodiecinema/director_movies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_id = self.kwargs['person_id']

        # 감독 정보 가져오기
        person_data = fetch_person_data(person_id)
        if person_data:
            context['person'] = person_data
        else:
            context['error'] = '해당 감독 정보를 가져오는 데 실패했습니다.'

        # 감독의 제작 영화 가져오기
        context['director_movies'] = get_director_movies(person_id)[:20]

        return context
    

class ReviewStatisticsView(TemplateView):
    template_name = 'moodiecinema/reviews_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs.get('movie_id')

        # 영화 정보 가져오기
        movie_data = get_movie_data(movie_id)
        if not movie_data:
            context['error'] = "영화 정보를 가져오는 데 실패했습니다."
            return context
        
        credits_data = get_movie_credits(movie_id)
        videos_data = get_movie_videos(movie_id)

        # 리뷰 데이터 가져오기 및 분석
        reviews = get_reviews_with_list_view(self.request, movie_id)
        review_analysis_data = analyze_reviews(reviews)

        # sentiment_count 데이터를 JSON 형식으로 변환
        sentiment_count_json = json.dumps(review_analysis_data['sentiment_count'])

        # 템플릿 컨텍스트에 데이터 추가
        context.update({
            'movie': movie_data,
            'credits': credits_data,
            'videos': videos_data,
            'sentiment_count_json': sentiment_count_json,  # JSON 데이터 추가
            **review_analysis_data  # 기존 리뷰 분석 데이터 추가
        })

        return context

