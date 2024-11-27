import json
import random
import requests
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import aiohttp
import re  # 정규 표현식 사용


class ChatbotAPIView(View):

    async def post(self, request):
        """
        사용자 요청을 처리하고 적절한 응답을 반환합니다.
        """
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'response': '메시지를 입력해주세요.'})

            # 의도 분석
            intent = self.analyze_intent(user_message)

            if intent == 'recommendation':
                response_text = self.get_movie_recommendations(user_message)
            elif intent == 'description':
                response_text = self.get_movie_description(user_message)
            else:
                response_text = await self.get_ollama_response(user_message)

            print(f"사용자 입력: {user_message}")
            print(f"분석된 의도: {intent}")
            print(f"생성된 응답: {response_text}")

            return JsonResponse({'response': response_text})
        except Exception as e:
            print(f"에러 발생: {e}")
            return JsonResponse({'response': f'서버에서 오류가 발생했습니다. {str(e)}'}, status=500)

    def analyze_intent(self, user_message):
        """
        메시지의 의도를 분석합니다.
        """
        user_message = user_message.lower()
        if any(keyword in user_message for keyword in ['추천', '영화 추천', '보고 싶어요', '장르']):
            return 'recommendation'
        elif any(keyword in user_message for keyword in ['설명', '줄거리']):
            return 'description'
        else:
            return 'general'

    def get_movie_recommendations(self, user_message):
        """
        TMDB API를 호출하여 영화 추천 목록을 반환합니다.
        """
        api_key = settings.TMDB_API_KEY
        if not api_key:
            return "TMDB API 키가 누락되어 영화를 추천할 수 없습니다."

        url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
            "language": "ko-KR",
        }

        genre_keywords = {
            '액션': 28,
            '드라마': 18,
            '코미디': 35,
            '모험': 12,
            '애니메이션': 16,
            '범죄': 80,
            '다큐멘터리': 99,
            '가족': 10751,
            '판타지': 14,
            '역사': 36,
            '공포': 27,
            '음악': 10402,
            '미스터리': 9648,
            '로맨스': 10749,
            'SF': 878,
            '스릴러': 53,
            '전쟁': 10752,
            '서부': 37
        }

        genre_id = None
        for keyword, genre in genre_keywords.items():
            if keyword in user_message:
                genre_id = genre
                break

        if genre_id:
            params["with_genres"] = genre_id

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                movies = data.get('results', [])
                if movies:
                    selected_movies = random.sample(movies, min(5, len(movies)))
                    genre_message = f"'{keyword}' 장르의 " if genre_id else "전체 "
                    return f"{genre_message}추천 영화 목록:\n" + "\n".join(
                        [f"- {movie['title']} ({movie.get('release_date', '개봉일 미정')})" for movie in selected_movies]
                    )
                else:
                    return "해당 장르에서 추천할 영화가 없습니다. 다른 장르를 요청해보세요!"
            else:
                return "영화 추천 정보를 가져오는 중 오류가 발생했습니다."
        except Exception as e:
            return f"영화 추천 요청 중 문제가 발생했습니다: {e}"

    def get_movie_description(self, user_message):
        """
        특정 영화의 줄거리, 감독, 출연진, 장르, 개봉일 정보를 반환합니다.
        """
        api_key = settings.TMDB_API_KEY
        if not api_key:
            return "TMDB API 키가 누락되어 영화 정보를 가져올 수 없습니다."

        movie_name = user_message.replace("설명해줘", "").replace("설명", "").replace("영화", "").strip()
        if not movie_name:
            return "영화 제목을 입력해주세요."

        search_url = "https://api.themoviedb.org/3/search/movie"
        search_params = {
            "api_key": api_key,
            "query": movie_name,
            "language": "ko-KR",
        }

        try:
            search_response = requests.get(search_url, params=search_params)
            if search_response.status_code != 200:
                return "영화를 검색하는 중 오류가 발생했습니다."

            search_results = search_response.json().get('results', [])
            if not search_results:
                return f"'{movie_name}'에 대한 정보를 찾을 수 없습니다."

            movie = search_results[0]
            movie_id = movie.get('id')
            title = movie.get('title', '제목 없음')
            overview = movie.get('overview', '줄거리 정보 없음')
            release_date = movie.get('release_date', '개봉일 미정')

            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            details_params = {
                "api_key": api_key,
                "language": "ko-KR",
                "append_to_response": "credits"
            }
            details_response = requests.get(details_url, params=details_params)
            if details_response.status_code != 200:
                return f"'{title}'의 상세 정보를 가져오는 중 오류가 발생했습니다."

            details = details_response.json()
            crew = details.get("credits", {}).get("crew", [])
            director = next((person.get("name") for person in crew if person.get("job") == "Director"), "정보 없음")

            cast = details.get("credits", {}).get("cast", [])
            top_cast = [actor.get("name", "정보 없음") for actor in cast[:3]]

            genres = details.get("genres", [])
            genre_names = [genre.get("name") for genre in genres]

            return (
                f"제목: {title}\n"
                f"줄거리: {overview}\n"
                f"감독: {director}\n"
                f"출연진: {', '.join(top_cast) or '정보 없음'}\n"
                f"장르: {', '.join(genre_names) or '정보 없음'}\n"
                f"개봉일: {release_date}"
            )
        except Exception as e:
            return f"영화 정보를 가져오는 중 오류가 발생했습니다: {e}"



    async def get_ollama_response(self, user_message):
        """
        Ollama를 사용하여 일반 대화 응답 생성.
        """
        try:
            base_url = "http://127.0.0.1:11434"  # Ollama 서버 주소
            request_data = {
                "model": "llama2:13b",
                "prompt": f"다음 질문에 한국어로 간단하고 정중하게 답변해주세요:\n{user_message}\n\n답변:",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{base_url}/api/generate", json=request_data) as response:
                    if response.status == 200:
                        # NDJSON 스트리밍 응답 처리
                        full_response = ""
                        async for line in response.content:
                            try:
                                decoded_line = json.loads(line.decode("utf-8"))
                                full_response += decoded_line.get("response", "").strip()
                            except json.JSONDecodeError:
                                continue  # 유효하지 않은 JSON 무시
                        
                        # 한글만 추출
                        korean_response = re.sub(r"[^가-힣\s.!?]", "", full_response)  # 한글, 공백, 구두점만 허용
                        korean_response = korean_response.strip()  # 양쪽 공백 제거
                        
                        # 첫 번째 문장만 반환
                        sentences = korean_response.split('.')  # 마침표로 문장 나누기
                        first_sentence = sentences[0].strip() if sentences else ""
                        if first_sentence:
                            return f"{first_sentence}."  # 첫 번째 문장 반환

                        return "제가 이해하지 못했습니다. 다시 말씀해주세요."
                    else:
                        return f"Ollama 서버 오류: {response.status}"
        except Exception as e:
            return f"Ollama 서버와 통신 중 오류가 발생했습니다: {e}"
