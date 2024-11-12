# moodiecinema/views.py
import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .bertgpusentiment import predict_sentiment

def home(request):
    api_key = settings.TMDB_API_KEY
    base_url = 'https://api.themoviedb.org/3'

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def analyze_sentiment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        print(f"Received content: {content}")  # 디버그 로그로 받은 콘텐츠 출력
        if content:
            sentiment = predict_sentiment(content)
            print(f"Predicted sentiment: {sentiment}")  # 디버그 로그로 예측된 감정 출력
            return JsonResponse({'sentiment': sentiment})
        else:
            print("No content received")  # 디버그 로그: content가 없을 때
    else:
        print("Invalid request method:", request.method)  # 디버그 로그: POST가 아닐 때
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
