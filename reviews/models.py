from django.db import models
from django.conf import settings
from movies.models import Movies
from .bertgpusentiment import predict_sentiment

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    rating = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 좋아요와 싫어요 필드 추가
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    emotion = models.CharField(max_length=10, blank=True, null=True)

    reported_count = models.IntegerField(default=0)
    is_reported = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # 리뷰가 새로 생성될 때만 감정 분석 수행
        if not self.emotion:
            self.emotion = predict_sentiment(self.content)  # 감정 분석 함수 호출
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review by {self.user} for {self.movie}"
    
class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_like = models.BooleanField()  # True for like, False for dislike

    class Meta:
        unique_together = ('review', 'user')  # 한 사용자당 하나의 리뷰에 대해 한 번만 반응 가능