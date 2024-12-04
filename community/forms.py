from django import forms
from .models import Post
from movies.models import Movies

# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post  # 연결할 모델
#         fields = ['title', 'content']  # 폼에서 사용할 필드
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목을 입력하세요'}),
#             'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '내용을 입력하세요', 'rows': 5}),
#         }


from django import forms
from .models import Post, Hashtag

class PostForm(forms.ModelForm):
    hashtags = forms.CharField(max_length=200, required=False, help_text="쉼표로 구분하여 해시태그 입력")

    class Meta:
        model = Post
        fields = ['title', 'content', 'hashtags']

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            hashtags = self.cleaned_data['hashtags']
            for title in hashtags.split(','):
                title = title.strip()
                if title:
                    # 영화 제목으로 Movie 객체를 검색
                    try:
                        movie = Movies.objects.get(title=title)
                        hashtag, created = Hashtag.objects.get_or_create(name=title, movie=movie)
                        post.hashtags.add(hashtag)
                    except Movies.DoesNotExist:
                        # 영화가 존재하지 않는 경우 사용자에게 알림을 추가하거나 무시
                        print(f"영화 '{title}'을(를) 찾을 수 없습니다.")
        return post
