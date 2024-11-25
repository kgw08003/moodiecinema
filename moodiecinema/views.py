import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .bertgpusentiment import predict_sentiment
from django.views.decorators.csrf import csrf_exempt

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