# userprofile/urls.py
from django.urls import path
from .views import MoviesByYearAPIView, MoviesByEraAPIView, TechAdvancementsAPIView, MovieTimelineAPIView

urlpatterns = [
    path('api/movies-by-year/', MoviesByYearAPIView.as_view(), name='movies_by_year'),
    path('api/movies-by-era/', MoviesByEraAPIView.as_view(), name='movies_by_era'),
    path('api/tech-advancements/', TechAdvancementsAPIView.as_view(), name='tech_advancements'),
    path('api/movie-timeline/', MovieTimelineAPIView.as_view(), name='movie_timeline'),
]
