# diary/urls.py
from django.urls import path
from .views import DiaryView, DiaryDetailView, DiaryCreateView
from . import views
from .views import DiaryView, DiaryDetailView, DiaryCreateView
from .views import DiaryMonthView

urlpatterns = [
    path('', DiaryView.as_view(), name='diary'),
    path('create/', DiaryCreateView.as_view(), name='diary_create'),
    path('detail/', DiaryDetailView.as_view(), name='diary_detail'),   
    path('month/', DiaryMonthView.as_view(), name='diary_month'),
]