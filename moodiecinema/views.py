# moodiecinema/views.py
import requests
from django.conf import settings
from django.shortcuts import render

def home(request):
    api_key = settings.TMDB_API_KEY
    base_url = 'https://api.themoviedb.org/3'

    # 다양한 카테고리에서 영화 가져오기
    popular_movies = requests.get(f'{base_url}/movie/popular?api_key={api_key}&language=ko-KR').json().get('results', [])
    trending_movies = requests.get(f'{base_url}/trending/movie/day?api_key={api_key}&language=ko-KR').json().get('results', [])
    recommended_movies = requests.get(f'{base_url}/movie/top_rated?api_key={api_key}&language=ko-KR').json().get('results', [])

    context = {
        'popular_movies': popular_movies,
        'trending_movies': trending_movies,
        'recommended_movies': recommended_movies,
    }
    return render(request, 'moodiecinema/home.html', context)