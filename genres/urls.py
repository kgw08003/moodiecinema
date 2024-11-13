from django.urls import path
from .views import CategoryView, GenreDetailView

app_name = 'genres'
urlpatterns = [
    path('category/', CategoryView.as_view(), name='category'),  # 카테고리 페이지
    path('genre/<int:genre_id>/', GenreDetailView.as_view(), name='genre_detail'),  # 장르별 영화 목록 페이지
]
