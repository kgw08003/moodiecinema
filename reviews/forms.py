# review/forms.py
from django import forms
from reviews.models import Review, ReviewReport

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': '리뷰를 작성해주세요'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'placeholder': '1-5 사이의 평점'}),
        }
