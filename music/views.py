from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
import requests
from diary.models import Diary

class MusicRecommendationView(View):
    def get(self, request):
        # 오늘 날짜의 일기에서 감정 분석 결과 가져오기
        today = timezone.now().date()  # 오늘 날짜

        # created_at 필드가 DateField일 경우, created_at=today로 비교
        latest_diary = Diary.objects.filter(user=request.user, created_at=today).first()

        if not latest_diary:
            return redirect('diary:create')  # 오늘 날짜의 일기가 없으면 일기 작성 페이지로 리디렉션

        emotion = latest_diary.emotion  # 감정 분석 결과
        print(f"감정 분석 결과: {emotion}")  # 로그를 찍어 확인

        # 감정에 맞는 음악 리스트를 Spotify에서 검색
        music_list = self.get_music_for_emotion(emotion)
        
        # 음악 리스트와 감정 값을 템플릿으로 전달
        return render(request, 'moodiecinema/recommendation.html', {
            'emotion': emotion,
            'music_list': music_list
        })

    def get_music_for_emotion(self, emotion):
        # Spotify API 요청 예제 (이전에 .env 파일에서 인증 정보 설정 필요)
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET

        # Spotify API 토큰 얻기
        auth_response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={'grant_type': 'client_credentials'},
            auth=(client_id, client_secret)
        )
        auth_data = auth_response.json()
        access_token = auth_data['access_token']

        # 감정별 검색 키워드 매핑 (한글 감정으로 수정)
        emotion_keyword_map = {
            '기쁨': 'uplifting movie soundtrack',  # 기쁨을 더 신나게 또는 부드럽게 유지
            '슬픔': 'comforting movie soundtrack',  # 슬픔에 공감하거나 위로를 주는 곡
            '분노': 'calming or empowering movie soundtrack',  # 차분함을 유도하거나 에너지 전환
            '공포': 'soothing or hopeful movie soundtrack',  # 안정감을 주는 곡
            '평온': 'relaxing or inspirational movie soundtrack',  # 평온함을 유지하거나 가볍게 고양
        }

        # 감정에 맞는 검색 키워드 선택
        search_query = emotion_keyword_map.get(emotion, 'movie soundtrack')
        # print(f"Spotify에서 검색할 키워드: {search_query}")  # 로그를 찍어 확인

        # 영화 OST만 검색하도록 추가적으로 'movie soundtrack' 키워드 포함
        search_query += ' movie soundtrack'

        # Spotify에서 감정에 맞는 음악(트랙) 검색
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(
            f'https://api.spotify.com/v1/search?q={search_query}&type=track&limit=10',
            headers=headers
        )
        data = response.json()

        # print(f"Spotify API 검색 결과: {data}")  # 로그를 찍어 확인

        # 트랙 정보에서 제목, 아티스트, Spotify URL을 추출하여 반환
        music_list = []
        for item in data['tracks']['items']:
            music_list.append({
                'title': item['name'],
                'artist': item['artists'][0]['name'],
                'spotify_url': item['external_urls']['spotify'],
                'album_image': item['album']['images'][0]['url'],  # 앨범 이미지 추가
            })
        
        return music_list
