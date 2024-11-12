from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100)  # 장르 이름
    genre_id = models.IntegerField(unique=True)  # API에서 제공되는 장르 ID

    def __str__(self):
        return self.name