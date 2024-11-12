from django import forms
from .models import User

class UserSignUpForm(forms.ModelForm): # 회원 로그인
    user_password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="비밀번호 확인")
    user_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': '생년월일 선택'}),
        label="생년월일"
    )

    class Meta:
        model = User
        fields = ['user_profile', 'user_name', 'user_email', 'user_birth', 'user_password']
        labels = {
            'user_profile': '프로필 사진',
            'user_name': '사용자 이름',
            'user_email': '이메일',
            'user_birth': '생년월일',
            'user_password': '비밀번호',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("user_password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned_data


class UserUpdateForm(forms.ModelForm): # 회원정보 수정
    user_password = forms.CharField(widget=forms.PasswordInput, label="비밀번호", required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="비밀번호 확인", required=False)
    user_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': '생년월일 선택'}),
        label="생년월일",
        required=False
    )

    class Meta:
        model = User
        fields = ['user_profile', 'user_email', 'user_birth', 'user_password']
        labels = {
            'user_profile': '프로필 사진',
            'user_email': '이메일',
            'user_birth': '생년월일',
            'user_password': '비밀번호',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("user_password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned_data
    


