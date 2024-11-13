# search/views.py
from django.shortcuts import render
from django.views import View
import requests

class MovieSearchView(View):
    template_name = 'moodiecinema/search_results.html'
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'  # 실제 API 키로 교체하세요

    def get(self, request):
        query = request.GET.get('q')
        page = request.GET.get('page', 1)  # 기본 페이지는 1
        movies = []
        total_pages = 1

        if query:
            response = requests.get(
                'https://api.themoviedb.org/3/search/movie',
                params={
                    'api_key': self.api_key,
                    'query': query,
                    'language': 'ko-KR',
                    'page': page  # 요청하는 페이지 번호
                }
            )
            data = response.json()
            movies = data.get('results', [])
            total_pages = data.get('total_pages', 1)

        return render(request, self.template_name, {
            'movies': movies,
            'query': query,
            'current_page': int(page),
            'total_pages': total_pages
        })
