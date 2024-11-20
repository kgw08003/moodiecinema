from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'reported_count', 'is_reported', 'created_at')
    list_filter = ('is_reported',)  # is_reported 필터 추가
    search_fields = ('user__user_name', 'content')  # 사용자 이름과 리뷰 내용으로 검색 가능

    # 신고된 리뷰만 표시하는 기능 추가
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_reported=True)  # 신고된 리뷰만 표시

admin.site.register(Review, ReviewAdmin)