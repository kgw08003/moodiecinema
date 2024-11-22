from reviews.views import ReviewListView
from collections import Counter
from itertools import chain
from django.db.models import Avg, Count

def get_reviews_with_list_view(request, movie_id):
    """ReviewListView를 통해 특정 영화의 리뷰 가져오기"""
    review_list_view = ReviewListView()
    review_list_view.request = request
    review_list_view.kwargs = {'movie_id': movie_id}
    queryset = review_list_view.get_queryset()
    return queryset

def analyze_reviews(reviews):
    """
    리뷰 데이터를 분석하여 감정 집계, 평점 통계, 워드 클라우드 데이터를 반환합니다.
    :param reviews: QuerySet 형태의 리뷰 리스트
    :return: 분석 결과 딕셔너리
    """
    if not reviews.exists():
        # 리뷰가 없을 경우 기본값 반환
        return {
            'sentiment_count': {},
            'total_sentiment': '감정 없음',
            'average_rating': None,
            'highest_rating_review': None,
            'lowest_rating_review': None,
            'emotion_percentage': {},
            'word_count': {},
            'rating_distribution': {},
            'author_statistics': [],
        }

    # 감정 집계
    emotions = [review.emotion for review in reviews if review.emotion]
    sentiment_count = Counter(emotions)
    most_common_sentiment = sentiment_count.most_common(1)

    # 총 감정 결과
    total_sentiment = most_common_sentiment[0][0] if most_common_sentiment else '감정 없음'

    # 평점 데이터 분석
    ratings = [review.rating for review in reviews if review.rating is not None]
    average_rating = sum(ratings) / len(ratings) if ratings else None
    highest_rating_review = max(reviews, key=lambda x: x.rating, default=None)
    lowest_rating_review = min(reviews, key=lambda x: x.rating, default=None)

    # 별점 분포 계산
    rating_distribution = Counter(ratings)

    # 감정 비율 계산
    total_reviews = len(reviews)
    emotion_percentage = {
        emotion: (count / total_reviews * 100) for emotion, count in sentiment_count.items()
    } if total_reviews > 0 else {}

    # 워드 클라우드 데이터 준비
    words = chain.from_iterable(
        review.content.split() for review in reviews if review.content
    )
    word_count = Counter(words)

    # 작성자별 통계 계산
    author_statistics = (
        reviews.values('user__user_name')
        .annotate(
            review_count=Count('id'),
            average_rating=Avg('rating')
        )
        .order_by('-review_count')
    )

    # 분석 결과 반환
    return {
        'sentiment_count': dict(sentiment_count),
        'total_sentiment': total_sentiment,
        'average_rating': average_rating,
        'highest_rating_review': highest_rating_review,
        'lowest_rating_review': lowest_rating_review,
        'emotion_percentage': emotion_percentage,
        'review_count': reviews.count(),  # 총 리뷰 수
        'word_count': dict(word_count.most_common(5)),  # 상위 5개 단어
        'rating_distribution': dict(rating_distribution),  # 별점 분포
        'author_statistics': list(author_statistics),  # 작성자 통계
    }