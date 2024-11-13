import requests
from django.shortcuts import render
from django.views import View
from .models import Genre

class CategoryView(View):
    def get(self, request):
        # DB에서 장르 정보를 조회
        genres = Genre.objects.all()

        # DB에 장르가 없으면 API 호출
        if not genres.exists():
            url = "https://api.themoviedb.org/3/genre/movie/list?language=ko"
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3ZTRhYzQyMjQ2YTkwODhmYjQ1ODVkZmQ3MjM2NGRjMiIsIm5iZiI6MTczMTI5ODkzNS4xNTI3NTUzLCJzdWIiOiI2NzMxODVhMGFkOGM5Y2NhY2UwNjM4NWIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.x06vR01K_Xwa5ND75LYJZKSHcLf7YCpEqHw0JDfXwG8"
            }
            response = requests.get(url, headers=headers)
            genre_data = response.json().get('genres', [])

            # API 응답이 있을 경우 DB에 저장
            for genre in genre_data:
                Genre.objects.update_or_create(
                    genre_id=genre['id'],
                    defaults={'name': genre['name']}
                )
            genres = Genre.objects.all()  # 새로 저장된 데이터를 다시 가져옴
        
        # 세션에 장르 목록 저장 (현재 동작 유지)
        request.session['genres'] = list(genres.values('genre_id', 'name'))

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

        # 세션 또는 DB에서 장르 이름 가져오기
        genre_name = next(
            (genre['name'] for genre in request.session.get('genres', []) if genre['genre_id'] == genre_id),
            Genre.objects.filter(genre_id=genre_id).first().name if Genre.objects.filter(genre_id=genre_id).exists() else "Unknown Genre"
        )

        return render(request, 'moodiecinema/genre_detail.html', {
            'movies': movies,
            'genre_name': genre_name,
            'total_pages': total_pages,
            'current_page': page,
            'genre_id': genre_id
        })
