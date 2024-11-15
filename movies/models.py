from django.db import models
from django.contrib.auth import get_user_model
import requests

User = get_user_model()

class Movies(models.Model):
    movie_id = models.IntegerField()  # TMDB 영화 ID
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 포스터 이미지 경로와 제목을 위한 새 필드
    poster_path = models.CharField(max_length=255, blank=True, null=True)  # 포스터 이미지 경로
    title = models.CharField(max_length=255, blank=True, null=True)  # 영화 제목

    def __str__(self):
        return f'{self.user.user_name} - {self.movie_id}'
    

    @classmethod
    def get_or_create_from_api(cls, movie_id, user):
        movie, created = cls.objects.get_or_create(movie_id=movie_id, defaults={'user': user})
        if created:
            # API 요청으로 영화 정보를 가져와서 등록
            api_key = '5f0eb3027f1b131897e4dcbe057e0931'  # 실제 API 키로 교체
            response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ko-KR')
            if response.status_code == 200:
                movie_data = response.json()
                movie.title = movie_data.get('title', '')
                movie.content = movie_data.get('overview', '')
                movie.poster_path = movie_data.get('poster_path', '')
                movie.save()
        return movie
