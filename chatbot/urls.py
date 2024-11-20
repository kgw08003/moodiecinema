# chatbot/urls.py
from django.urls import path
from .views import ChatbotAPIView

urlpatterns = [
    path('api/', ChatbotAPIView.as_view(), name='chatbot_api'),
]