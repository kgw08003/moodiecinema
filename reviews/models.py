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
    #is_active = models.BooleanField(default=True)  # 리뷰 활성화 여부

    def save(self, *args, **kwargs):
        # 리뷰가 새로 생성될 때만 감정 분석 수행
        if not self.emotion:
            self.emotion = predict_sentiment(self.content)  # 감정 분석 함수 호출
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.user_name}의 리뷰: {self.content[:20]}"
    
class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_like = models.BooleanField()  # True for like, False for dislike

    class Meta:
        unique_together = ('review', 'user')  # 한 사용자당 하나의 리뷰에 대해 한 번만 반응 가능


class ReviewReport(models.Model):
    REVIEW_REPORT_REASONS = [
        ('spam', '도배성 게시물'),
        ('inappropriate', '부적절한 내용'),
        ('false_info', '거짓 정보'),
    ]

    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='reports')  # 신고된 리뷰
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 신고자
    reason = models.CharField(max_length=50, choices=REVIEW_REPORT_REASONS)  # 신고 사유
    reported_at = models.DateTimeField(auto_now_add=True)  # 신고 일시
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Report for Review {self.review.id} by {self.reported_by.user_name}"

    
    