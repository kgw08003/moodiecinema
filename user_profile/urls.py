# userprofile/urls.py
from django.urls import path
from .views import MoviesByYearAPIView, MoviesByEraAPIView, TechAdvancementsAPIView, MovieTimelineAPIView, GenreRatingsAPIView, RemakeMoviesAPIView, RemakeMoviesRevenueAPIView

urlpatterns = [
    path('api/movies-by-year/', MoviesByYearAPIView.as_view(), name='movies_by_year'),
    path('api/movies-by-era/', MoviesByEraAPIView.as_view(), name='movies_by_era'),
    path('api/tech-advancements/', TechAdvancementsAPIView.as_view(), name='tech_advancements'),
    path('api/movie-timeline/', MovieTimelineAPIView.as_view(), name='movie_timeline'),
    path('api/genre-ratings/', GenreRatingsAPIView.as_view(), name='genre_ratings'),
    path('api/remake-movies/', RemakeMoviesAPIView.as_view(), name='remake_movies'),
    path('api/remake-revenues/', RemakeMoviesRevenueAPIView.as_view(), name='remake-revenues'),
]
