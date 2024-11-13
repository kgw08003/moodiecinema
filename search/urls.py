# search/urls.py
from django.urls import path
from .views import MovieSearchView

urlpatterns = [
    path('', MovieSearchView.as_view(), name='movie_search'),
]
