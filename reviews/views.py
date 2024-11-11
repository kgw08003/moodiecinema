from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from reviews import models
from .models import Review, Movies,ReviewLike

from rest_framework import viewsets, permissions,status
from .serializers import ReviewSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import ReviewForm

from django.http import JsonResponse



class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    permission_classes = [permissions.IsAuthenticated]  # 로그인된 사용자만 허용
    def perform_create(self, serializer):
      serializer.save(user=self.request.user)


class FeedbackAnalysisView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_reviews = Review.objects.count()
        avg_rating = Review.objects.aggregate(models.Avg('rating'))['rating__avg']
        data = {
            'total_reviews': total_reviews,
            'average_rating': avg_rating,
        }
        return Response(data)


class ReviewListView(ListView):
    model = Review
    template_name = 'moodiecinema/movie.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        # 특정 영화의 리뷰만 필터링
        movie_id = self.kwargs.get('movie_id')
        return Review.objects.filter(movie__movie_id=movie_id)
    

class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        movie_id = self.kwargs.get('movie_id')
        movie = Movies.get_or_create_from_api(movie_id, self.request.user)
        form.instance.movie = movie
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        # 리뷰 생성 후 이동할 URL 설정
        return reverse('movie_detail', kwargs={'movie_id': self.kwargs['movie_id']})
    
class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'moodiecinema/review_form.html'
    
    def get_success_url(self):
        return reverse_lazy('reviews_manage')  # 수정 후 리뷰 관리 페이지로 리디렉션

    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user  # 작성자만 수정 가능

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'moodiecinema/confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('reviews_manage')  # 삭제 후 리뷰 관리 페이지로 리디렉션

    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user  # 작성자만 삭제 가능

class ReviewsManageView(LoginRequiredMixin, TemplateView):
    template_name = 'moodiecinema/reviews_manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(user=self.request.user)
        return context
    

class LikeReviewView(APIView):
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        user = request.user

        # 좋아요 상태 확인 및 처리
        review_like, created = ReviewLike.objects.get_or_create(review=review, user=user, defaults={'is_like': True})
        
        if not created and review_like.is_like:
            # 이미 좋아요를 누른 경우 -> 좋아요 취소
            review_like.delete()
            review.like_count -= 1
        elif not created:
            # 싫어요를 누른 상태에서 좋아요로 변경
            review_like.is_like = True
            review_like.save()
            review.like_count += 1
            review.dislike_count -= 1
        else:
            # 처음으로 좋아요를 누르는 경우
            review.like_count += 1

        review.save()
        return Response({'like_count': review.like_count, 'dislike_count': review.dislike_count}, status=status.HTTP_200_OK)


class DislikeReviewView(APIView):
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        user = request.user

        # 싫어요 상태 확인 및 처리
        review_like, created = ReviewLike.objects.get_or_create(review=review, user=user, defaults={'is_like': False})
        
        if not created and not review_like.is_like:
            # 이미 싫어요를 누른 경우 -> 싫어요 취소
            review_like.delete()
            review.dislike_count -= 1
        elif not created:
            # 좋아요를 누른 상태에서 싫어요로 변경
            review_like.is_like = False
            review_like.save()
            review.like_count -= 1
            review.dislike_count += 1
        else:
            # 처음으로 싫어요를 누르는 경우
            review.dislike_count += 1

        review.save()
        return Response({'like_count': review.like_count, 'dislike_count': review.dislike_count}, status=status.HTTP_200_OK)
    