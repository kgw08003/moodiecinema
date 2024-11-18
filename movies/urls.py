from django.urls import path 
from .views import MovieDetailView, ActorMoviesView, DirectorMoviesView

urlpatterns = [
    path('<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('actor/<int:person_id>/', ActorMoviesView.as_view(), name='actor_movies'),
    path('director/<int:person_id>/', DirectorMoviesView.as_view(), name='director_movies'),
    
]
