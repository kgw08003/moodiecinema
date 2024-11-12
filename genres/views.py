# genres/views.py

import requests
from django.shortcuts import render
from django.views import View
from .models import Genre  # genres 앱의 Genre 모델 임포트

class CategoryView(View):
    def get(self, request):
        # TMDb API에서 영화 장르 목록 가져오기
        url = "https://api.themoviedb.org/3/genre/movie/list?language=ko"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3ZTRhYzQyMjQ2YTkwODhmYjQ1ODVkZmQ3MjM2NGRjMiIsIm5iZiI6MTczMTI5ODkzNS4xNTI3NTUzLCJzdWIiOiI2NzMxODVhMGFkOGM5Y2NhY2UwNjM4NWIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.x06vR01K_Xwa5ND75LYJZKSHcLf7YCpEqHw0JDfXwG8"
        }
        response = requests.get(url, headers=headers)
        genres = response.json().get('genres', [])

        # 디버그: 장르 목록 출력
        print("Genres:", genres)

        # DB에 장르 정보 저장
        for genre in genres:
            Genre.objects.update_or_create(
                genre_id=genre['id'],
                defaults={'name': genre['name']}
            )

        # 세션에 장르 목록 저장 (선택사항)
        request.session['genres'] = [{'id': genre['id'], 'name': genre['name']} for genre in genres]

        # 템플릿에 장르 목록 전달
        return render(request, 'moodiecinema/category.html', {'genres': genres})

class GenreDetailView(View):
    def get(self, request, genre_id):
        # 페이지 번호를 받아오기, 기본값은 1
        page = request.GET.get('page', 1)
        page = int(page)

        # TMDb API로 해당 장르의 영화 목록 가져오기 (page 파라미터 추가)
        url = f"https://api.themoviedb.org/3/discover/movie?with_genres={genre_id}&language=ko&page={page}"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3ZTRhYzQyMjQ2YTkwODhmYjQ1ODVkZmQ3MjM2NGRjMiIsIm5iZiI6MTczMTI5ODkzNS4xNTI3NTUzLCJzdWIiOiI2NzMxODVhMGFkOGM5Y2NhY2UwNjM4NWIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.x06vR01K_Xwa5ND75LYJZKSHcLf7YCpEqHw0JDfXwG8"
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        # 영화 목록 추출
        movies = data.get('results', [])
        total_pages = data.get('total_pages', 1)

        # DB에서 해당 장르의 이름을 가져오기
        genre_name = next(
            (genre.name for genre in Genre.objects.all() if genre.genre_id == genre_id),
            "Unknown Genre"
        )

        # 장르 이름과 영화 목록을 템플릿에 전달
        return render(request, 'moodiecinema/genre_detail.html', {
            'movies': movies,
            'genre_name': genre_name,
            'total_pages': total_pages,
            'current_page': page,
            'genre_id': genre_id
        })
    

