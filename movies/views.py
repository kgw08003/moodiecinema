from django.views.generic import TemplateView
from django.shortcuts import render
import requests
from reviews.views import ReviewListView, ReviewCreateView
from .models import Movies

class MovieDetailView(TemplateView):
    template_name = 'moodiecine/movies.html'
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'
    base_url = 'https://api.themoviedb.org/3/movie/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs['movie_id']
        
        # API 데이터 수집
        movie_data = self.get_movie_data(movie_id)
        credits_data = self.get_movie_credits(movie_id)
        videos_data = self.get_movie_videos(movie_id)
        
        if not movie_data:
            context['error'] = '영화 정보를 가져오는 데 실패했습니다.'
            return context

        # 데이터 구성
        context['movie'] = movie_data
        context['cast'] = credits_data.get('cast', [])[:5] if credits_data else []
        context['director'] = credits_data.get('director')
        
        genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
        context['similar_movies'] = (self.get_similar_movies_from_tmdb(genre_ids) or [])[:8]

        youtube_videos = [video for video in videos_data.get('results', []) if video['site'] == 'YouTube']
        context['youtube_trailers'] = youtube_videos[:2] if youtube_videos else None

        # TMDB 리뷰
        tmdb_reviews_response = requests.get(f'{self.base_url}{movie_id}/reviews', params={
            'api_key': self.api_key,
            'language': 'en-US'
        })
        if tmdb_reviews_response.status_code == 200:
            context['tmdb_reviews'] = tmdb_reviews_response.json().get('results', [])
        else:
            context['tmdb_reviews'] = []

        # 사용자 리뷰
        review_list_view = ReviewListView()
        review_list_view.kwargs = {'movie_id': movie_id}
        context['reviews'] = review_list_view.get_queryset()
        context['review_form'] = ReviewCreateView.form_class()

        return context

    def get_movie_data(self, movie_id):
        try:
            response = requests.get(f'{self.base_url}{movie_id}', params={'api_key': self.api_key, 'language': 'ko-KR'})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {e}")
        return None

    def get_movie_credits(self, movie_id):
        try:
            response = requests.get(f'{self.base_url}{movie_id}/credits', params={'api_key': self.api_key, 'language': 'ko-KR'})
            response.raise_for_status()
            credits = response.json()
            cast = credits.get('cast', [])
            crew = credits.get('crew', [])
            for actor in cast:
                actor['profile_image_url'] = f"https://image.tmdb.org/t/p/w200{actor['profile_path']}" if actor.get('profile_path') else '/static/images/default-profile.png'
            director = next((member for member in crew if member['job'] == 'Director'), None)
            if director:
                director['profile_image_url'] = f"https://image.tmdb.org/t/p/w200{director['profile_path']}" if director.get('profile_path') else '/static/images/default-profile.png'
            return {'cast': cast, 'director': director}
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {e}")
        return None

    def get_movie_videos(self, movie_id):
        try:
            response = requests.get(f'{self.base_url}{movie_id}/videos', params={'api_key': self.api_key, 'language': 'ko-KR'})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {e}")
        return {}

    def get_similar_movies_from_tmdb(self, genre_ids):
        try:
            response = requests.get("https://api.themoviedb.org/3/discover/movie", params={
                'api_key': self.api_key,
                'with_genres': ','.join(map(str, genre_ids)),
                'language': 'ko-KR'
            })
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {e}")
        return []


class ActorMoviesView(TemplateView):
    template_name = 'moodiecine/actor_movies.html'
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_id = self.kwargs['person_id']
        
        # API 데이터 수집
        person_data = self.get_person_data(person_id)
        cast_movies = self.get_cast_movies(person_id)

        if person_data:
            context['person'] = person_data
        else:
            context['error'] = '해당 배우 정보를 가져오는 데 실패했습니다.'

        context['cast_movies'] = cast_movies[:20]
        return context

    def get_person_data(self, person_id):
        response = requests.get(f'https://api.themoviedb.org/3/person/{person_id}', params={'api_key': self.api_key, 'language': 'ko-KR'})
        if response.status_code == 200:
            person = response.json()
            person['profile_image_url'] = f"https://image.tmdb.org/t/p/w300{person['profile_path']}" if person['profile_path'] else '/static/images/default-profile.png'
            return person
        return None

    def get_cast_movies(self, person_id):
        response = requests.get(f'https://api.themoviedb.org/3/person/{person_id}/movie_credits', params={'api_key': self.api_key, 'language': 'ko-KR'})
        if response.status_code == 200:
            credits = response.json()
            cast_movies = sorted(credits.get('cast', []), key=lambda x: x.get('release_date', ''), reverse=True)
            return cast_movies
        return []


class DirectorMoviesView(TemplateView):
    template_name = 'moodiecine/director_movies.html'
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_id = self.kwargs['person_id']
        
        # API 데이터 수집
        person_data = self.get_person_data(person_id)
        director_movies = self.get_director_movies(person_id)

        if person_data:
            context['person'] = person_data
        else:
            context['error'] = '해당 감독 정보를 가져오는 데 실패했습니다.'

        context['director_movies'] = director_movies[:20]
        return context

    def get_person_data(self, person_id):
        response = requests.get(f'https://api.themoviedb.org/3/person/{person_id}', params={'api_key': self.api_key, 'language': 'ko-KR'})
        if response.status_code == 200:
            person = response.json()
            person['profile_image_url'] = f"https://image.tmdb.org/t/p/w300{person['profile_path']}" if person['profile_path'] else '/static/images/default-profile.png'
            return person
        return None

    def get_director_movies(self, person_id):
        response = requests.get(f'https://api.themoviedb.org/3/person/{person_id}/movie_credits', params={'api_key': self.api_key, 'language': 'ko-KR'})
        if response.status_code == 200:
            credits = response.json()
            director_movies = sorted(
                [movie for movie in credits.get('crew', []) if movie['job'] == 'Director'],
                key=lambda x: x.get('release_date', ''), reverse=True
            )
            return director_movies
        return []
