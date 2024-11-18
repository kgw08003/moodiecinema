# userprofile/views.py
from django.http import JsonResponse
from django.views import View
import requests
from django.conf import settings

class MoviesByYearAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        start_year = 1980
        end_year = 2030  # 2020년대와 향후 데이터를 포함
        years = list(range(start_year, end_year + 1))
        movie_counts = []

        for year in years:
            url = f"https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": api_key,
                "primary_release_year": year,
                "page": 1
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                movie_counts.append(data.get("total_results", 0))
            else:
                movie_counts.append(0)

        return JsonResponse({"years": years, "counts": movie_counts})

class MoviesByEraAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        eras = ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        era_ranges = [
            (1950, 1959), (1960, 1969), (1970, 1979),
            (1980, 1989), (1990, 1999), (2000, 2009),
            (2010, 2019), (2020, 2029)
        ]
        counts = []
        popular_genres = []

        # TMDB 장르 ID와 이름 매핑
        genre_map = {
            28: '액션',
            18: '드라마',
            35: '코미디',
            12: '모험',
            16: '애니메이션',
            80: '범죄',
            99: '다큐멘터리',
            10751: '가족',
            14: '판타지',
            36: '역사',
            27: '공포',
            10402: '음악',
            9648: '미스터리',
            10749: '로맨스',
            878: 'SF',
            10770: 'TV 영화',
            53: '스릴러',
            10752: '전쟁',
            37: '서부'
        }

        for start_year, end_year in era_ranges:
            total_movies = 0
            genre_count = {}

            for year in range(start_year, end_year + 1):
                url = f"https://api.themoviedb.org/3/discover/movie"
                params = {
                    "api_key": api_key,
                    "primary_release_year": year,
                    "page": 1
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    total_movies += data.get("total_results", 0)

                    # Count genres
                    for movie in data.get("results", []):
                        for genre in movie.get("genre_ids", []):
                            genre_count[genre] = genre_count.get(genre, 0) + 1

            counts.append(total_movies)
            if genre_count:
                # Get the most popular genre in the era and map it to the name
                most_popular_genre_id = max(genre_count, key=genre_count.get)
                popular_genres.append(genre_map.get(most_popular_genre_id, "Unknown"))
            else:
                popular_genres.append("Unknown")

        return JsonResponse({"eras": eras, "counts": counts, "popular_genres": popular_genres})

class TechAdvancementsAPIView(View):
    def get(self, request):
        advancements = [
            {"year": 1903, "description": "최초의 내러티브 영화 - '대열차 강도'"},
            {"year": 1927, "description": "첫 유성 영화 '재즈 싱어'"},
            {"year": 1939, "description": "컬러 영화 '오즈의 마법사'"},
            {"year": 1952, "description": "최초의 와이드스크린 영화 '비원'"},
            {"year": 1977, "description": "'스타워즈' - 미니어처와 모션 컨트롤 카메라 혁신"},
            {"year": 1982, "description": "'트론' - 대규모 CGI 사용"},
            {"year": 1993, "description": "'쥬라기 공원' - CGI와 실물 효과의 결합"},
            {"year": 1995, "description": "CGI 기술 발전 - '토이 스토리'"},
            {"year": 1999, "description": "'매트릭스' - 불릿 타임 기술"},
            {"year": 2001, "description": "'반지의 제왕' - 퍼포먼스 캡처"},
            {"year": 2009, "description": "3D 영화 '아바타' 혁신"},
            {"year": 2013, "description": "'그래비티' - 실사와 CGI의 결합"},
            {"year": 2016, "description": "'정글북' - 포토리얼리즘 CGI"},
            {"year": 2020, "description": "'테넷' - 시간 역행 효과"}
        ]
        return JsonResponse(advancements, safe=False)

class MovieTimelineAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        page = int(request.GET.get("page", 1))  # 현재 페이지 (기본값: 1)
        url = f"https://api.themoviedb.org/3/movie/top_rated"
        movies = []

        params = {
            "api_key": api_key,
            "language": "ko-kr",
            "page": page  # 요청된 페이지 번호
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            for movie in data.get("results", []):
                movies.append({
                    "year": movie["release_date"][:4],
                    "movie": movie["title"],
                    "rating": movie["vote_average"]
                })

            # 페이지네이션 정보
            total_pages = data.get("total_pages", 1)
            current_page = data.get("page", 1)
            return JsonResponse({
                "movies": movies,
                "total_pages": total_pages,
                "current_page": current_page
            })
        else:
            return JsonResponse({"error": "Failed to fetch timeline data"}, status=500)
