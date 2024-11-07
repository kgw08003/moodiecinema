# moodiecinema/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .bertgpusentiment import predict_sentiment

def home(request):
    return render(request, 'moodiecinema/home.html')

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def analyze_sentiment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        print(f"Received content: {content}")  # 디버그 로그로 받은 콘텐츠 출력
        if content:
            sentiment = predict_sentiment(content)
            print(f"Predicted sentiment: {sentiment}")  # 디버그 로그로 예측된 감정 출력
            return JsonResponse({'sentiment': sentiment})
        else:
            print("No content received")  # 디버그 로그: content가 없을 때
    else:
        print("Invalid request method:", request.method)  # 디버그 로그: POST가 아닐 때
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
