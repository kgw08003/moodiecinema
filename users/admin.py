from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'user_email', 'admin', 'user_birth', 'user_profile_display')  # 사용자 정보 보여주기
    search_fields = ('user_name', 'user_email')  # 검색할 수 있는 필드
    list_filter = ('admin',)  # admin 필드로 필터링

    def user_profile_display(self, obj):
        if obj.user_profile:
            return mark_safe(f'<img src="{obj.user_profile.url}" style="width: 50px; height: 50px;"/>')
        return "No Image"
    user_profile_display.short_description = 'Profile Image'  # 열 제목 설정

admin.site.register(User, UserAdmin)  # 사용자 모델을 관리자에 등록
