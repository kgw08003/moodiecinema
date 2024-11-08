from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView
from .forms import UserSignUpForm, UserUpdateForm
from .models import User


class SignUpView(FormView):  # 클래스 이름을 SignUpView로 수정
    template_name = 'moodiecinema/signup.html'
    form_class = UserSignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['user_password'])
        user.save()
        return super().form_valid(form)
    
from django.views.generic import TemplateView

class UserProfileView(TemplateView):
    template_name = 'moodiecinema/profile.html'  # 프로필 페이지 템플릿 경로

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def custom_logout(request):
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    request.session['logged_out'] = True
    return redirect('home')  # 메인 페이지로 리디렉션

 
class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'moodiecinema/update_profile.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save(commit=False)

        # 비밀번호 변경 시 해시하여 저장
        new_password = form.cleaned_data.get('user_password')
        if new_password:
            user.set_password(new_password)

        user.save()
        return super().form_valid(form)
    
    def get_object(self, queryset=None):
        return self.request.user  # 현재 로그인된 사용자 객체 반환
    
class CategoryView(TemplateView):
    template_name = 'moodiecinema/category.html'

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')
        if request.user.check_password(password):
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, "회원 탈퇴가 완료되었습니다.")
            return redirect('home')  # 탈퇴 후 홈 페이지로 이동
        else:
            messages.error(request, "비밀번호가 틀렸습니다. 다시 시도해주세요.")
            return redirect('profile')  # 비밀번호가 틀린 경우 프로필 페이지로 다시 이동

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

class DiaryDetailView(LoginRequiredMixin, View):
    def get(self, request):
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': '날짜가 제공되지 않았습니다.'}, status=400)

        try:
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': '잘못된 날짜 형식입니다.'}, status=400)

        # 선택된 날짜와 일치하는 일기 필터링
        diaries = Diary.objects.filter(user=request.user, created_at=selected_date).order_by('-created_at')

        if not diaries.exists():
            return JsonResponse({'error': '해당 날짜의 일기를 찾을 수 없습니다.'}, status=404)

        diary_list = [{
            'title': diary.title,
            'content': diary.content,
            'emotion': getattr(diary, 'emotion', None)
        } for diary in diaries]

        return JsonResponse({'diaries': diary_list})
    
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