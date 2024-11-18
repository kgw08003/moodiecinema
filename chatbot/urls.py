from django.urls import path
from .views import MovieChatbotHTMLView, MovieChatbotView

urlpatterns = [
    path('', MovieChatbotHTMLView.as_view(), name='chatbot'),  # 채팅봇 페이지 경로
    path('api/', MovieChatbotView.as_view(), name='chatbot_api'),  # 챗봇 API 경로
]