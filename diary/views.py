from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Diary
from .forms import DiaryForm
from django.http import JsonResponse
from django.views import View

class DiaryView(LoginRequiredMixin, ListView):
    template_name = 'moodiecinema/diary.html'
    context_object_name = 'diaries'

    def get_queryset(self):
        # 파라미터에서 날짜를 받아오거나 기본적으로 오늘 날짜를 사용
        date_str = self.request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
        selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

        # `created_at` 필드와 `selected_date`를 사용하여 필터링
        return Diary.objects.filter(user=self.request.user, created_at=selected_date)
    
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from .models import Diary
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

from moodiecinema.bertgpusentiment import predict_sentiment


import logging
logger = logging.getLogger(__name__)

class DiaryDetailView(LoginRequiredMixin, View):
    def get(self, request):
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': '날짜가 제공되지 않았습니다.'}, status=400)

        try:
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': '잘못된 날짜 형식입니다.'}, status=400)

        # 선택한 날짜에 해당하는 일기 불러오기
        diary = Diary.objects.filter(user=request.user, created_at=selected_date).first()
        if not diary:
            return JsonResponse({'error': '해당 날짜의 일기를 찾을 수 없습니다.'}, status=404)

        # 감정 분석이 저장되어 있지 않다면 분석 후 저장
        if not diary.emotion or diary.emotion == "긍정":  # 기존에 '긍정'으로 잘못 저장된 경우 갱신
            diary.emotion = predict_sentiment(diary.content)
            diary.save()
            logger.info(f"Predicted emotion for '{diary.content}': {diary.emotion}")

        diary_data = {
            'title': diary.title,
            'content': diary.content,
            'emotion': diary.emotion or '분석 결과 없음'
        }

        return JsonResponse({'diary': diary_data})
    
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Diary
from django.views import View
import json

@method_decorator(csrf_exempt, name='dispatch')
class DiaryCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            date = data.get('date')
            content = data.get('content')
            emotion = data.get('emotion')

            if not date or not content:
                return JsonResponse({'error': '날짜와 내용을 입력해야 합니다.'}, status=400)

            # 같은 날짜의 일기 중 최신 일기만 남기고 업데이트
            existing_diaries = Diary.objects.filter(user=request.user, created_at=timezone.datetime.strptime(date, '%Y-%m-%d').date()).order_by('-created_at')
            
            if existing_diaries.exists():
                latest_diary = existing_diaries.first()
                latest_diary.content = content
                latest_diary.emotion = emotion
                latest_diary.save()
                # 중복된 일기 삭제
                existing_diaries.exclude(pk=latest_diary.pk).delete()
            else:
                Diary.objects.create(
                    user=request.user,
                    created_at=timezone.datetime.strptime(date, '%Y-%m-%d').date(),
                    content=content,
                    title="일기",
                    emotion=emotion
                )

            return JsonResponse({'message': '일기가 저장되었습니다.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 데이터 형식입니다.'}, status=400)