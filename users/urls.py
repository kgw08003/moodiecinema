from django.urls import path
from django.contrib.auth.views import LoginView
from . import views


urlpatterns = [
    path('login/', LoginView.as_view(template_name='moodiecinema/login.html'), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

]