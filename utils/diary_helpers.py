from collections import defaultdict
from datetime import datetime
from diary.models import Diary  # Diary 모델 임포트

def analyze_diary_emotions(user):
    """
    사용자 일기 데이터를 분석하여 날짜별 감정 추세 데이터를 반환합니다.
    """
    diaries = Diary.objects.filter(user=user).order_by('created_at')  # 사용자별 일기 정렬
    emotion_trend = defaultdict(lambda: defaultdict(int))  # {날짜: {감정: 개수}}

    for diary in diaries:
        # created_at에서 날짜만 추출
        date = diary.created_at.astimezone().date()  # 날짜만 추출 (시간대 변환)
        emotion_trend[date][diary.emotion] += 1

    # JSON 형식 데이터 생성
    trend_labels = list(emotion_trend.keys())  # 날짜 리스트
    emotions = ['기쁨', '슬픔', '분노', '평온', '공포']  # 감정 종류
    emotion_data = {emotion: [emotion_trend[date].get(emotion, 0) for date in trend_labels] for emotion in emotions}

    return {
        'trend_labels': trend_labels,
        'emotion_data': emotion_data,
        'emotions': emotions,
    }
