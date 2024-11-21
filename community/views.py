from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment

# 게시글 목록
class PostListView(ListView):
    model = Post
    template_name = 'moodiecinema/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

# 게시글 작성
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'moodiecinema/post_form.html'
    success_url = reverse_lazy('community:post_list')  # URL 하드코딩 제거

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# 게시글 상세 보기
class PostDetailView(DetailView):
    model = Post
    template_name = 'moodiecinema/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 부모 댓글만 필터링
        context['parent_comments'] = self.object.comments.filter(parent=None)
        context['request'] = self.request  # 템플릿에서 request 사용 가능
        return context

# 게시글 삭제
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'moodiecinema/post_confirm_delete.html'

    def get_success_url(self):
        # 게시글 삭제 후 커뮤니티 메인 페이지로 이동
        return reverse_lazy('community:post_list')

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if post.user != request.user:
            # 작성자가 아닌 경우 에러 템플릿 렌더링
            return JsonResponse({'error': '삭제 권한이 없습니다.'}, status=403)
        return super().delete(request, *args, **kwargs)

# 댓글 작성
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'moodiecinema/comment_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])

        # 대댓글인 경우 처리
        parent_id = self.kwargs.get('parent_id')
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.post.get_absolute_url()

# 댓글 삭제
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'moodiecinema/comment_confirm_delete.html'

    def get_success_url(self):
        # 댓글 삭제 후 게시글 상세 페이지로 이동
        return self.object.post.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            # 작성자가 아닌 경우 에러 템플릿 렌더링
            return JsonResponse({'error': '삭제 권한이 없습니다.'}, status=403)
        return super().delete(request, *args, **kwargs)

# 좋아요 토글
def toggle_like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})
