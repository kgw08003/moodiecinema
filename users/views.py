from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView
from .forms import UserSignUpForm, UserUpdateForm
from .models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings


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
        
User = get_user_model()

class FindUsernameView(View):
    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(user_email=email).first()

        if user:
            send_mail(
                '아이디 찾기',
                f'귀하의 아이디는: {user.user_name}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, '아이디가 이메일로 전송되었습니다.')
        else:
            messages.error(request, '해당 이메일로 등록된 아이디가 없습니다.')
        return redirect('login')
    
    def get(self, request):
        return render(request, 'moodiecinema/find_username.html')

class PasswordResetRequestView(View):
    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(user_email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f'/users/password-reset/{uid}/{token}/')  # URL 수정

            send_mail(
                '비밀번호 재설정 요청',
                f'다음 링크를 통해 비밀번호를 재설정하세요: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, '비밀번호 재설정 링크가 이메일로 전송되었습니다.')
        else:
            messages.error(request, '해당 이메일로 등록된 계정이 없습니다.')
        return redirect('login')
    
    def get(self, request):
        return render(request, 'moodiecinema/password_reset_request.html')
    
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import update_session_auth_hash

class PasswordResetView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return render(request, 'moodiecinema/password_reset.html', {'validlink': True, 'uidb64': uidb64, 'token': token})
        else:
            messages.error(request, '링크가 유효하지 않거나 만료되었습니다.')
            return redirect('password_reset_request')

    def post(self, request, uidb64, token):
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect(request.path)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            messages.success(request, '비밀번호가 성공적으로 재설정되었습니다.')
            return redirect('login')
        else:
            messages.error(request, '링크가 유효하지 않거나 만료되었습니다.')
            return redirect('password_reset_request')