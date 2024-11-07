from django.urls import path
from .views import SignUpView, UserProfileView, custom_logout, UserUpdateView, CategoryView, DeleteAccountView
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='moodiecinema/login.html'), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', custom_logout, name='logout'), # custom_logout 사용
    path('profile/update/', UserUpdateView.as_view(), name='update_profile'),
    path('category/', CategoryView.as_view(), name='category'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete_account'),
    path('diary/', views.DiaryView.as_view(), name='diary'),
]
