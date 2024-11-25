# userprofile/urls.py
from django.urls import path
from .views import MoviesByYearAPIView, MoviesByEraAPIView, TechAdvancementsAPIView, MovieTimelineAPIView
from .views import GenreRatingsAPIView, RemakeMoviesAPIView, RemakeMoviesRevenueAPIView, MoviesByCountryAPIView, MoviesByAgeRatingAPIView
from . import views

urlpatterns = [
    path('api/movies-by-year/', MoviesByYearAPIView.as_view(), name='movies_by_year'),
    path('api/movies-by-era/', MoviesByEraAPIView.as_view(), name='movies_by_era'),
    path('api/tech-advancements/', TechAdvancementsAPIView.as_view(), name='tech_advancements'),
    path('api/movie-timeline/', MovieTimelineAPIView.as_view(), name='movie_timeline'),
    path('api/genre-ratings/', GenreRatingsAPIView.as_view(), name='genre_ratings'),
    path('api/remake-movies/', RemakeMoviesAPIView.as_view(), name='remake_movies'),
    path('api/remake-revenues/', RemakeMoviesRevenueAPIView.as_view(), name='remake-revenues'),
    path('api/movies-by-country/', MoviesByCountryAPIView.as_view(), name='movies_by_country'),
    path('api/movies-by-age-rating/', MoviesByAgeRatingAPIView.as_view(), name='movies-by-age-rating'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]   
