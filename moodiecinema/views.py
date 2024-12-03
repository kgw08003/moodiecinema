import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .bertgpusentiment import predict_sentiment
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta,datetime

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
    
    # HttpResponse 객체로 반환
    return render(request, 'moodiecinema/home.html', context)

def fetch_movies(url,params,max_results=20):
    """
    특정 날짜 범위 내에서 개봉 예정 영화를 TMDB API를 통해 가져오는 함수.
    """
    movies = []
    page = 1
    while len(movies) < max_results:
        # API 요청
        params['page'] = page
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"API 요청 실패: {response.status_code}")
            break  # 요청 실패 시 루프 종료
        
        data = response.json()
        results = data.get('results', [])
        
        # 포스터가 있는 영화만 추가
        for movie in results:
            if movie.get('poster_path'):  # 포스터가 있는 영화만
                movies.append(movie)
                if len(movies) >= max_results:
                    break
        
        if page >= data.get('total_pages', 1):  # 마지막 페이지에 도달하면 종료
            break
        page += 1

    return movies[:max_results]

def upcoming_movies(request):
    """
    TMDB API를 사용하여 이번 달과 다음 달의 개봉 예정 영화 데이터를 가져오는 함수.
    """
    # TMDB API 키와 기본 URL 설정
    api_key = settings.TMDB_API_KEY
    base_url = 'https://api.themoviedb.org/3'
    url = f"{base_url}/discover/movie"

    # 오늘 날짜 및 이번 달/다음 달 날짜 계산
    today = datetime.now()

    # 이번 달 마지막 날 (다음 달 첫날 - 1일)
    next_month = today.replace(day=28) + timedelta(days=4)  # 이번 달의 마지막 날을 얻기 위한 방법
    last_day_of_this_month = next_month.replace(day=1) - timedelta(days=1)

    # 다음 달 첫날
    first_day_of_next_month = last_day_of_this_month + timedelta(days=1)

    # 다음 달 마지막 날 (이번 달의 마지막 날 + 1달 - 1일)
    next_month_last_day = (first_day_of_next_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # 이번 달 데이터 가져오기
    params_this_month = {
        'api_key': api_key,
        'language': 'ko-KR',
        'region':'KR',
        'with_original_language': 'ko',
        'primary_release_date.gte': today.strftime('%Y-%m-%d'),  # 오늘 이후
        'primary_release_date.lte': last_day_of_this_month.strftime('%Y-%m-%d'),# 이번 달 말일까지
    }
    
    upcoming_movies_this_month = fetch_movies(url, params_this_month)

    # 이번 달 영화만 포함 (날짜 필터링)
    upcoming_movies_this_month = [
        movie for movie in upcoming_movies_this_month
        if movie['release_date'] and 
        datetime.strptime(movie['release_date'], '%Y-%m-%d').date() > today.date() and
        datetime.strptime(movie['release_date'], '%Y-%m-%d').date() <= last_day_of_this_month.date()
    ]

    # 다음 달 데이터 가져오기
    params_next_month = {
        'api_key': api_key,
        'language': 'ko-KR',
        'region':'KR',
        'with_original_language': 'ko',
        'primary_release_date.gte': first_day_of_next_month.strftime('%Y-%m-%d'),  # 다음 달 첫날
        'primary_release_date.lte': next_month_last_day.strftime('%Y-%m-%d'),  # 다음 달 마지막 날
    }

    upcoming_movies_next_month = fetch_movies(url, params_next_month)
    # 다음 달 영화만 포함 (날짜 필터링)
    upcoming_movies_next_month = [
        movie for movie in upcoming_movies_next_month
        if movie['release_date'] and 
        datetime.strptime(movie['release_date'], '%Y-%m-%d').date() >= first_day_of_next_month.date() and
        datetime.strptime(movie['release_date'], '%Y-%m-%d').date() <= next_month_last_day.date()
    ]
    
    # 날짜 기준으로 정렬 (날짜 오름차순)
    upcoming_movies_this_month.sort(key=lambda x: datetime.strptime(x['release_date'], '%Y-%m-%d').date())
    upcoming_movies_next_month.sort(key=lambda x: datetime.strptime(x['release_date'], '%Y-%m-%d').date())

    # context에 영화 데이터 추가
    context = {
        'upcoming_movies_this_month': upcoming_movies_this_month,
        'upcoming_movies_next_month': upcoming_movies_next_month,
    }
    
    print(len(upcoming_movies_this_month))  # 이번 달 영화 개수 출력
    print(len(upcoming_movies_next_month))  # 다음 달 영화 개수 출력

    return render(request, 'moodiecinema/upcoming_movies.html', context)

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


from django.views.generic import ListView
from movies.models import Movies  # Movie 모델 가져오기

class SearchView(ListView):
    model = Movies
    template_name = 'moodiecinema/search_results.html'  # 템플릿 파일 경로 설정
    context_object_name = 'results'  # 템플릿에서 사용할 객체 이름

    def get_queryset(self):
        query = self.request.GET.get('query')  # GET 방식으로 전달된 검색어 가져오기
        if query:
            return Movies.objects.filter(title__icontains=query)  # 제목에 검색어가 포함된 영화 필터링
        else:
            return Movies.objects.none()  # 검색어가 없을 때 빈 QuerySet 반환

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query')  # 검색어를 컨텍스트에 추가
        return context


from django.views.generic import DetailView
from movies.models import Movies

class MovieDetailView(DetailView):
    model = Movies
    template_name = 'moodiecinema/movie_detail.html'
    context_object_name = 'movie'
    