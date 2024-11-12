
from django import forms
from .models import Diary

class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['title', 'content']  # 감정 분석 결과는 뷰에서 추가