from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Jjim
from movies.models import Movies
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import requests

@login_required
def add_to_wishlist(request, movie_id):
    user = request.user
    
    # Movies 모델에서 영화 데이터를 가져오거나 API를 통해 생성
    movie = Movies.get_or_create_from_api(movie_id, user)

    # 이미 찜 목록에 있는지 확인
    if not Jjim.objects.filter(user=user, movie=movie).exists():
        Jjim.objects.create(user=user, movie=movie)
        return JsonResponse({'success': True, 'message': '영화가 찜 목록에 추가되었습니다.'})
    
    return JsonResponse({'success': False, 'message': '이미 찜 목록에 추가된 영화입니다.'})

@login_required
def remove_from_wishlist(request, movie_id):
    user = request.user
    
    try:
        # 찜 목록에서 영화 제거
        jjim = Jjim.objects.get(user=user, movie__movie_id=movie_id)
        jjim.delete()
        return JsonResponse({'success': True, 'message': '영화가 찜 목록에서 제거되었습니다.'})
    except Jjim.DoesNotExist:
        return JsonResponse({'success': False, 'message': '찜 목록에서 찾을 수 없는 영화입니다.'})

@login_required
def wishlist(request):
    # 현재 로그인한 사용자의 찜 목록 가져오기
    jjims = Jjim.objects.filter(user=request.user)
    movies = [jjim.movie for jjim in jjims]
    return render(request, 'moodiecinema/wishlist.html', {'movies': movies})
