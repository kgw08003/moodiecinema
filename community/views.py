from django.views.generic import ListView, CreateView, DetailView, View
from django.views.generic.edit import DeleteView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotFound, JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment, Hashtag
from .forms import PostForm
from movies.models import Movies
from django.contrib import messages



# 게시글 목록
class PostListView(ListView):
    model = Post
    template_name = 'moodiecinema/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # 정렬 추가
        return Post.objects.order_by('-created_at')  # 최신순 정렬

class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'moodiecinema/post_form.html'
    success_url = reverse_lazy('community:post_list')

    def form_valid(self, form):
        # 현재 사용자 설정
        form.instance.user = self.request.user

        # 게시물 저장
        response = super().form_valid(form)

        # 해시태그 처리
        hashtags = self.request.POST.get('hashtag', '').split(',')
        for name in hashtags:
            name = name.strip()  # 공백 제거
            if name:
                # 영화 검색
                movie = Movies.objects.filter(title__iexact=name).first()
                if movie:
                    # 해시태그 생성 또는 가져오기
                    hashtag, created = Hashtag.objects.get_or_create(name=name)
                    hashtag.movies.add(movie)  # 해시태그와 영화 연결
                    form.instance.hashtags.add(hashtag)  # 게시물과 해시태그 연결
                else:
                    # 영화가 없는 경우 경고 메시지 표시
                    messages.warning(self.request, f"영화 '{name}'을(를) 찾을 수 없습니다.")

        return response


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
    
class PostEditView(UpdateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        # 폼 데이터가 유효하면 저장
        post = form.save(commit=False)
        post.save()

        # 수정 완료 후 JSON 응답 반환 (모달창에서 처리)
        return JsonResponse({'success': True, 'message': '게시글이 수정되었습니다.'})

    def form_invalid(self, form):
        # 폼 데이터가 유효하지 않을 경우 JSON 응답 반환
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
# 게시글 삭제
class PostDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            post = self.get_object()

            # 권한 확인: 작성자만 삭제 가능
            if post.user != request.user:
                return JsonResponse({'success': False, 'error': '삭제 권한이 없습니다.'}, status=403)

            # 삭제 처리
            post.delete()

            # JSON 응답 반환
            return JsonResponse({'success': True, 'message': '게시글이 삭제되었습니다.'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def get_object(self):
        from .models import Post  # 필요한 경우 적절히 모델을 import
        from django.shortcuts import get_object_or_404

        # URL에서 pk를 통해 Post 객체 가져오기
        return get_object_or_404(Post, pk=self.kwargs.get('pk'))

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
class CommentDeleteView(View):
    def post(self, request, post_id, comment_id):
        # 댓글 객체 가져오기
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, user=request.user)
        
        try:
            comment.delete()  # 댓글 삭제
            return JsonResponse({'success': True, 'message': '댓글이 삭제되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

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

class HashtagRedirectView(View):
    def get(self, request, hashtag_name):
        # 영화 제목을 기준으로 영화 객체 가져오기
        movie = Movies.objects.filter(title__iexact=hashtag_name).first()  # 대소문자 구분 없이 검색
        if movie:
            # 영화 상세 페이지로 리디렉션
            return redirect('movies:movie_detail', movie_id=movie.movie_id)
        else:
            # 영화가 없는 경우 404 반환
            return HttpResponseNotFound(f"'{hashtag_name}'에 해당하는 영화가 없습니다.")