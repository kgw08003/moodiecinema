"""
URL configuration for moodiecinema project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from moodiecinema import views
from django.conf.urls.static import static
from django.conf import settings
from jjim import views as jjim_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.cover,name='cover'),
    path('home/', views.home, name='home'),
    path('users/', include('users.urls')),  # users 앱의 urls.py 포함
    path('diary/', include('diary.urls')),  # 다이어리 관련 URL 포함
    path('auth/', include('social_django.urls', namespace='social')),
    path('analyze_sentiment/', views.analyze_sentiment, name='analyze_sentiment'),
    path('movies/', include('movies.urls')), 
    path('reviews/',include('reviews.urls')),
    path('genres/', include('genres.urls')),  # 'genres' 앱의 URL을 포함
    path('search/', include('search.urls')),
    path('music/', include('music.urls')), 
    path('wishlist/', include('jjim.urls')),  # jjim 앱의 URL 포함
    path('userprofile/', include('user_profile.urls')),
    path('chatbot/', include('chatbot.urls')),  # chatbot 앱의 URL 포함
    path('community/', include('community.urls')),  # Community 앱 추가
    path('upcoming/', views.upcoming_movies, name='upcoming_movies'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)