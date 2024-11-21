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

class GenreRatingsAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
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
        genres_data = []

        for genre_id, genre_name in genre_map.items():
            url = f"https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": api_key,
                "with_genres": genre_id,
                "vote_count.gte": 10,  # 최소한의 평점 수 필터링
                "sort_by": "vote_average.desc"
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                ratings = [movie["vote_average"] for movie in data.get("results", [])]
                if ratings:
                    genres_data.append({
                        "genre": genre_name,
                        "average_rating": sum(ratings) / len(ratings),
                        "max_rating": max(ratings),
                        "min_rating": min(ratings)
                    })
        
        return JsonResponse(genres_data, safe=False)


class RemakeMoviesAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3"

        # 사전에 정의된 리메이크 영화 리스트 (리메이크와 원작 타이틀 쌍)
        predefined_remakes = [
            {"remake_title": "Let Me In", "original_title": "Let the Right One In"},
            {"remake_title": "The Departed", "original_title": "Infernal Affairs"},
            {"remake_title": "Oldboy", "original_title": "Oldeuboi"},
            {"remake_title": "Insomnia", "original_title": "Insomnia"},
            {"remake_title": "Scarface", "original_title": "Scarface"},
            {"remake_title": "A Fistful of Dollars", "original_title": "Yojimbo"},
            {"remake_title": "The Magnificent Seven", "original_title": "Seven Samurai"},
            {"remake_title": "12 Monkeys", "original_title": "La Jetée"},
            {"remake_title": "True Lies", "original_title": "La Totale!"},
            {"remake_title": "The Birdcage", "original_title": "La Cage aux Folles"},
        ]

        remake_comparison = []
        for pair in predefined_remakes:
            # 원작 영화 검색 (한국어)
            url = f"{base_url}/search/movie"
            params = {"api_key": api_key, "query": pair["original_title"], "language": "ko-KR"}
            original_response = requests.get(url, params=params)
            
            # 리메이크 영화 검색 (한국어)
            params = {"api_key": api_key, "query": pair["remake_title"], "language": "ko-KR"}
            remake_response = requests.get(url, params=params)

            if original_response.status_code == 200 and remake_response.status_code == 200:
                original_data = original_response.json()
                remake_data = remake_response.json()

                if original_data["results"] and remake_data["results"]:
                    # 가장 적합한 결과를 필터링 (예: 개봉 연도)
                    original_movie = next(
                        (movie for movie in original_data["results"]
                        if "release_date" in movie and "1997" in movie["release_date"]),
                        original_data["results"][0]
                    )
                    remake_movie = next(
                        (movie for movie in remake_data["results"]
                        if "release_date" in movie and "2002" in movie["release_date"]),
                        remake_data["results"][0]
                    )

                    remake_comparison.append({
                        "remake_title": remake_movie["title"],
                        "original_title": original_movie["title"],
                        "remake_vote_average": remake_movie["vote_average"],
                        "original_vote_average": original_movie["vote_average"]
                    })

        return JsonResponse(remake_comparison, safe=False)


class RemakeMoviesRevenueAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3"

        predefined_remakes = [
            {"remake_title": "Let Me In", "original_title": "Let the Right One In"},
            {"remake_title": "The Departed", "original_title": "Infernal Affairs"},
            {"remake_title": "Oldboy", "original_title": "Oldeuboi"},
            {"remake_title": "The Magnificent Seven", "original_title": "Seven Samurai"},
            {"remake_title": "The Birdcage", "original_title": "La Cage aux Folles"},
        ]

        remake_comparison = []
        for pair in predefined_remakes:
            # 원작 영화 검색
            original_response = requests.get(
                f"{base_url}/search/movie",
                params={"api_key": api_key, "query": pair["original_title"], "language": "ko-KR"}
            )
            # 리메이크 영화 검색
            remake_response = requests.get(
                f"{base_url}/search/movie",
                params={"api_key": api_key, "query": pair["remake_title"], "language": "ko-KR"}
            )

            if original_response.status_code == 200 and remake_response.status_code == 200:
                original_data = original_response.json()
                remake_data = remake_response.json()

                if original_data["results"] and remake_data["results"]:
                    # 원작과 리메이크 영화 ID 가져오기
                    original_movie = original_data["results"][0]
                    remake_movie = remake_data["results"][0]

                    # 원작 영화 상세 정보
                    original_details_response = requests.get(
                        f"{base_url}/movie/{original_movie['id']}",
                        params={"api_key": api_key, "language": "ko-KR"}
                    )
                    # 리메이크 영화 상세 정보
                    remake_details_response = requests.get(
                        f"{base_url}/movie/{remake_movie['id']}",
                        params={"api_key": api_key, "language": "ko-KR"}
                    )

                    if original_details_response.status_code == 200 and remake_details_response.status_code == 200:
                        original_details = original_details_response.json()
                        remake_details = remake_details_response.json()

                        # 수익 데이터를 비교하여 추가
                        original_revenue = original_details.get("revenue", 0)
                        remake_revenue = remake_details.get("revenue", 0)

                        remake_comparison.append({
                            "remake_title": remake_details["title"],
                            "original_title": original_details["title"],
                            "remake_revenue": remake_revenue,
                            "original_revenue": original_revenue,
                        })

        return JsonResponse(remake_comparison, safe=False)


# 국가별 영화 개봉 수량 (TMDB api기준)
class MoviesByCountryAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3/discover/movie"
        country_codes = {
        "US": "en", "KR": "ko", "FR": "fr", "JP": "ja", "IN": "hi",
        "CN": "zh", "DE": "de", "GB": "en", "IT": "it", "ES": "es",
        "RU": "ru", "BR": "pt", "MX": "es", "AU": "en", "CA": "en",
        "AR": "es", "TR": "tr", "SA": "ar", "NG": "en", "ZA": "en",
        "EG": "ar", "ID": "id", "TH": "th", "VN": "vi", "PH": "en"
    }
  # 국가 코드와 언어 매핑

        country_data = {}

        for country, language in country_codes.items():
            response = requests.get(
                base_url,
                params={
                    "api_key": api_key,
                    "region": country,  # 지역 필터
                    "with_original_language": language,  # 언어 필터
                    "sort_by": "release_date.desc",
                    "primary_release_date.gte": "1900-01-01",
                    "primary_release_date.lte": "2024-12-31",
                },
            )
            if response.status_code == 200:
                data = response.json()
                # 국가별 개봉 수량 저장
                country_data[country] = data.get("total_results", 0)
            else:
                print(f"Failed to fetch data for {country}: {response.status_code}")
                country_data[country] = 0

        # 디버깅 로그
        print("Country data: ", country_data)

        return JsonResponse(country_data)

# 연령대별 선호 영화
class MoviesByAgeRatingAPIView(View):
    def get(self, request):
        api_key = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3/discover/movie"
        certification_levels = ["G", "PG", "PG-13", "R", "NC-17"]  # 연령 등급
        country = "US"  # 미국 기준 연령 등급

        age_rating_data = {}

        for certification in certification_levels:
            response = requests.get(
                base_url,
                params={
                    "api_key": api_key,
                    "certification_country": country,
                    "certification": certification,
                    "sort_by": "vote_average.desc",  # 높은 평점 기준 정렬
                    "vote_count.gte": 10,  # 최소 10개 이상의 투표가 있는 영화만
                    "primary_release_date.gte": "2000-01-01",  # 2000년 이후 개봉
                    "primary_release_date.lte": "2024-12-31",
                    "language": "ko-KR",  # 한국어로 번역된 제목 가져오기
                },
            )
            if response.status_code == 200:
                data = response.json()
                age_rating_data[certification] = [
                    {
                        "title": movie.get("title", movie.get("original_title")),
                        "vote_average": movie["vote_average"],
                    }
                    for movie in data["results"]
                ]
            else:
                age_rating_data[certification] = []

        return JsonResponse(age_rating_data)
