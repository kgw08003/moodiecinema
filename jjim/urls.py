# jjim/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add-to-wishlist/<int:movie_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:movie_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('', views.wishlist, name='wishlist'),
]
