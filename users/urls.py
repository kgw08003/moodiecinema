from django.urls import path
from .views import SignUpView, UserProfileView, custom_logout, UserUpdateView, CategoryView, DeleteAccountView
from django.contrib.auth.views import LoginView
from .views import FindUsernameView, PasswordResetRequestView, PasswordResetView

urlpatterns = [
    path('login/', LoginView.as_view(template_name='moodiecinema/login.html'), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', custom_logout, name='logout'), # custom_logout 사용
    path('profile/update/', UserUpdateView.as_view(), name='update_profile'),
    path('category/', CategoryView.as_view(), name='category'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete_account'),
    path('find-username/', FindUsernameView.as_view(), name='find_username'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetView.as_view(), name='password_reset'),
]
