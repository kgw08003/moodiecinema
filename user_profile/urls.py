from django.urls import path
from .views import MoviesByYearAPIView, MoviesByEraAPIView, TechAdvancementsAPIView, MovieTimelineAPIView, SelfStatisticsAPIView, SelfStatisticsView
from .views import GenreRatingsAPIView, RemakeMoviesAPIView, RemakeMoviesRevenueAPIView, MoviesByCountryAPIView, MoviesByAgeRatingAPIView
from . import views


urlpatterns = [
    path('api/movies-by-year/', MoviesByYearAPIView.as_view(), name='movies_by_year'),
    path('api/movies-by-era/', MoviesByEraAPIView.as_view(), name='movies_by_era'),
    path('api/tech-advancements/', TechAdvancementsAPIView.as_view(), name='tech_advancements'),
    path('api/movie-timeline/', MovieTimelineAPIView.as_view(), name='movie_timeline'),
    path('api/genre-ratings/', GenreRatingsAPIView.as_view(), name='genre_ratings'),
    path('api/remake-movies/', RemakeMoviesAPIView.as_view(), name='remake_movies'),
    path('api/remake-revenues/', RemakeMoviesRevenueAPIView.as_view(), name='remake_revenues'),
    path('api/movies-by-country/', MoviesByCountryAPIView.as_view(), name='movies_by_country_api'),  # 수정
    path('api/movies-by-age-rating/', MoviesByAgeRatingAPIView.as_view(), name='movies_by_age_rating_api'),  # 수정
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('self-statistics/', SelfStatisticsView.as_view(), name='self_statistics'),  # 템플릿 렌더링
    path('api/self-statistics/', SelfStatisticsAPIView.as_view(), name='self_statistics_api'),  # API
    path('api/remake-movies/', RemakeMoviesAPIView.as_view(), name='remake_movies_api'),
    path('api/remake-revenues/', RemakeMoviesRevenueAPIView.as_view(), name='remake_revenue_api'),
]
