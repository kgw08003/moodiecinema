# review/urls.py
from django.urls import path
from .views import ReviewListView, ReviewCreateView,ReviewUpdateView,ReviewDeleteView,ReviewsManageView

urlpatterns = [
    path('movie/<int:movie_id>/reviews/', ReviewListView.as_view(), name='review_list'),  # 리뷰 리스트
    path('movie/<int:movie_id>/reviews/new/', ReviewCreateView.as_view(), name='review_create'),  # 리뷰 작성
    path('review/<int:pk>/update/', ReviewUpdateView.as_view(), name='edit_review'),
    path('profile/review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='delete_review'),
    path('profile/reviews/manage/', ReviewsManageView.as_view(), name='reviews_manage'),
]
