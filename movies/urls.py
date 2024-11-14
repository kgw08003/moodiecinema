from django.urls import path
from .views import MovieDetailView

urlpatterns = [
    path('<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),
    
]