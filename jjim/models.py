from django.db import models
from django.contrib.auth.models import User
from movies.models import Movies # 찜 목록에 추가할 영화 모델

from django.conf import settings

class Jjim(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # settings.AUTH_USER_MODEL로 수정
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"