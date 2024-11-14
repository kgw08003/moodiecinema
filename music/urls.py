from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('recommendation/', views.MusicRecommendationView.as_view(), name='recommendation'),

]
