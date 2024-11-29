from django.urls import path
from .views import (
    PostListView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    CommentCreateView,
    CommentDeleteView,
    toggle_like_post,
)

app_name = 'community'

urlpatterns = [
    # 게시글 목록
    path('', PostListView.as_view(), name='post_list'),
    
    # 게시글 작성
    path('new/', PostCreateView.as_view(), name='post_create'),
    
    # 게시글 상세 보기
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    
    # 게시글 삭제
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    
    # 댓글 작성 (최상위 댓글)
    path('<int:post_id>/comment/', CommentCreateView.as_view(), name='comment_create'),
    
    # 대댓글 작성
    path('<int:post_id>/comment/<int:parent_id>/', CommentCreateView.as_view(), name='comment_reply'),
    
    # 댓글 삭제
    path('<int:post_id>/comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    
    # 좋아요 토글
    path('<int:post_id>/like/', toggle_like_post, name='toggle_like'),

]
