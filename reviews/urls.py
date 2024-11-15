# review/urls.py
from django.urls import path
from .views import ReviewListView, ReviewCreateView,ReviewUpdateView,ReviewDeleteView,ReviewsManageView,LikeReviewView,DislikeReviewView, ReviewReportAPIView

urlpatterns = [
    path('movie/<int:movie_id>/reviews/', ReviewListView.as_view(), name='review_list'),  # 리뷰 리스트
    path('movie/<int:movie_id>/reviews/new/', ReviewCreateView.as_view(), name='review_create'),  # 리뷰 작성
    path('review/<int:pk>/update/', ReviewUpdateView.as_view(), name='edit_review'),
    path('profile/review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='delete_review'),
    path('profile/reviews/manage/', ReviewsManageView.as_view(), name='reviews_manage'),
    path('review/<int:review_id>/like/', LikeReviewView.as_view(), name='like_review'), 
    path('review/<int:review_id>/dislike/', DislikeReviewView.as_view(), name='dislike_review'),  
    path('review/<int:review_id>/report/', ReviewReportAPIView.as_view(), name='report_review'),
]
