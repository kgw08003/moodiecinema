from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import UserSignUpForm

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
    template_name = 'users/profile.html'  # 프로필 페이지 템플릿 경로

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def custom_logout(request):
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    request.session['logged_out'] = True
    return redirect('home')  # 메인 페이지로 리디렉션