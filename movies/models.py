from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Movies(models.Model):
    movie_id = models.IntegerField()  # TMDB 영화 ID
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.movie_id}'
