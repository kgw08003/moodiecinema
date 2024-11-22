from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Diary
from .forms import DiaryForm
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from moodiecinema.bertgpusentiment import predict_sentiment
import json
import logging
import random
import requests

# 감정별 카테고리 매핑
EMOTION_CATEGORY_MAP = {
    '기쁨': [35, 878, 12, 16, 10749, 10402, 14],  # 코미디, SF, 모험, 애니메이션, 로맨스, 음악, 판타지
    '슬픔': [18, 16, 35, 10402],                  # 드라마, 애니메이션, 코미디, 음악
    '분노': [10752, 28, 36, 80, 37],              # 전쟁, 액션, 역사, 범죄, 서부
    '공포': [9648, 53, 10752, 14, 27, 878],       # 미스터리, 스릴러, 전쟁, 판타지, 공포, SF
    '평온': [10770, 10751, 99, 10751, 16, 10402]  # 힐링, 가족, 다큐멘터리, 가족, 애니, 음악
}

logger = logging.getLogger(__name__)

class DiaryView(LoginRequiredMixin, ListView):
    template_name = 'moodiecinema/diary.html'
    context_object_name = 'diaries'

    def get_queryset(self):
        date_str = self.request.GET.get('date')
        if date_str:
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            selected_date = timezone.now().date()
        return Diary.objects.filter(user=self.request.user, created_at=selected_date)

class DiaryDetailView(LoginRequiredMixin, View):
    def get(self, request):
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': '날짜가 제공되지 않았습니다.'}, status=400)

        try:
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            print("Requested Date:", selected_date)
        except ValueError:
            return JsonResponse({'error': '잘못된 날짜 형식입니다.'}, status=400)

        diary = Diary.objects.filter(user=request.user, created_at=selected_date).first()
        if not diary:
            return JsonResponse({'error': '해당 날짜의 일기를 찾을 수 없습니다.'}, status=404)

        # 감정에 따른 카테고리 설정
        emotion = diary.emotion
        categories = EMOTION_CATEGORY_MAP.get(emotion, [])
        recommended_movies = []

        # 각 카테고리에서 무작위로 영화를 10개 선택
        for category in categories:
            url = f"https://api.themoviedb.org/3/discover/movie?with_genres={category}&language=ko"
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3ZTRhYzQyMjQ2YTkwODhmYjQ1ODVkZmQ3MjM2NGRjMiIsIm5iZiI6MTczMTI5ODkzNS4xNTI3NTUzLCJzdWIiOiI2NzMxODVhMGFkOGM5Y2NhY2UwNjM4NWIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.x06vR01K_Xwa5ND75LYJZKSHcLf7YCpEqHw0JDfXwG8"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print("API 요청 실패:", response.status_code, response.text)
            else:
                movies = response.json().get('results', [])
                recommended_movies.extend(movies)

        # 영화 10개 무작위로 선택
        random.shuffle(recommended_movies)
        recommended_movies = recommended_movies[:10]

        diary_data = {
            'title': diary.title,
            'content': diary.content,
            'emotion': diary.emotion or '분석 결과 없음',
            'recommended_movies': recommended_movies
        }

        # print("Recommended Movies for", selected_date, ":", recommended_movies) # 활성화시 일기장에 불러오는 영화 정보 cmd 창에 나옴

        return JsonResponse({'diary': diary_data})

@method_decorator(csrf_exempt, name='dispatch')
class DiaryCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            date = data.get('date')
            content = data.get('content')

            if not date or not content:
                return JsonResponse({'error': '날짜와 내용을 입력해야 합니다.'}, status=400)

            # 감정 분석 수행
            emotion = predict_sentiment(content)

            # 같은 날짜의 일기 중 최신 일기만 남기고 업데이트
            selected_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
            existing_diaries = Diary.objects.filter(user=request.user, created_at=selected_date).order_by('-created_at')
            
            if existing_diaries.exists():
                latest_diary = existing_diaries.first()
                latest_diary.content = content
                latest_diary.emotion = emotion
                latest_diary.save()
            else:
                Diary.objects.create(
                    user=request.user,
                    created_at=selected_date,
                    content=content,
                    title="일기",
                    emotion=emotion
                )

            return JsonResponse({'message': '일기가 저장되었습니다.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 데이터 형식입니다.'}, status=400)


class DiaryMonthView(LoginRequiredMixin, View):
    def get(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not year or not month:
            return JsonResponse({'error': '연도와 월이 필요합니다.'}, status=400)
        
        diaries = Diary.objects.filter(
            user=request.user,
            created_at__year=year,
            created_at__month=month
        ).values('created_at', 'emotion')
        
        diary_data = {diary['created_at'].strftime('%Y-%m-%d'): diary['emotion'] for diary in diaries}
        return JsonResponse({'diaries': diary_data})