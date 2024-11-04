# urls.py
from django.urls import path
from .views import SignUpView, UserProfileView, custom_logout  # custom_logout 뷰 임포트
from django.contrib.auth.views import LoginView



urlpatterns = [
    path('login/', LoginView.as_view(template_name='moodiecinema/login.html'), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', custom_logout, name='logout'),  # custom_logout 사용
]
