from django.shortcuts import render
from django.views import View
import requests

class MovieSearchView(View):
    template_name = 'moodiecinema/search_results.html'
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'  # 실제 API 키로 교체하세요

    def get(self, request):
        query = request.GET.get('q')
        page = request.GET.get('page', 1)
        selected_genres = request.GET.getlist('genre')
        actor_name = request.GET.get('actor')
        director_name = request.GET.get('director')
        genres = self.get_genre_list()
        movies = []
        total_pages = 1

        # 배우 및 감독 ID 가져오기
        actor_id = self.get_person_id(actor_name) if actor_name else None
        director_id = self.get_person_id(director_name) if director_name else None

        # 1. 영화 제목으로 검색
        if query:
            response = requests.get(
                'https://api.themoviedb.org/3/search/movie',
                params={
                    'api_key': self.api_key,
                    'query': query,
                    'language': 'ko-KR',
                    'page': page
                }
            )
            data = response.json()
            movies = data.get('results', [])
            total_pages = data.get('total_pages', 1)

            # 2. 영화 제목 검색 결과가 없을 때 배우 및 감독으로 검색
            if not movies:
                person_response = requests.get(
                    'https://api.themoviedb.org/3/search/person',
                    params={
                        'api_key': self.api_key,
                        'query': query,
                        'language': 'ko-KR',
                        'page': page
                    }
                )
                person_data = person_response.json()
                people = person_data.get('results', [])

                # 배우나 감독의 영화 목록 추가
                if people:
                    for person in people:
                        if query.lower() in person['name'].lower():
                            # known_for 필드와 get_movie_credits 결과를 모두 추가
                            known_for_movies = person.get('known_for', [])
                            full_movie_credits = self.get_movie_credits(person['id'])

                            # 중복 없이 영화 추가
                            for movie in known_for_movies + full_movie_credits:
                                if movie not in movies:
                                    movies.append(movie)

        # 3. 장르, 배우, 감독을 기준으로 검색 (query가 없는 경우)
        elif selected_genres or actor_id or director_id:
            params = {
                'api_key': self.api_key,
                'with_genres': ','.join(selected_genres) if selected_genres else None,
                'with_cast': actor_id if actor_id else None,
                'with_crew': director_id if director_id else None,
                'language': 'ko-KR',
                'page': page
            }
            response = requests.get(
                'https://api.themoviedb.org/3/discover/movie',
                params=params
            )
            data = response.json()
            movies = data.get('results', [])
            total_pages = data.get('total_pages', 1)

        return render(request, self.template_name, {
            'movies': movies,
            'query': query,
            'genres': genres,
            'selected_genres': selected_genres,
            'actor_name': actor_name,
            'director_name': director_name,
            'current_page': int(page),
            'total_pages': total_pages
        })

    def get_genre_list(self):
        """TMDb API에서 장르 목록을 가져오는 함수"""
        response = requests.get(
            'https://api.themoviedb.org/3/genre/movie/list',
            params={'api_key': self.api_key, 'language': 'ko-KR'}
        )
        data = response.json()
        return data.get('genres', [])

    def get_person_id(self, name):
        """배우 또는 감독 이름으로 TMDb API에서 해당 인물 ID를 가져옴"""
        if not name:
            return None
        response = requests.get(
            'https://api.themoviedb.org/3/search/person',
            params={
                'api_key': self.api_key,
                'query': name,
                'language': 'ko-KR'
            }
        )
        data = response.json()
        person = data.get('results', [])
        if not person:
            print(f"'{name}'에 대한 검색 결과가 없습니다.")
            return None
        return person[0]['id']

    def get_movie_credits(self, person_id):
        """특정 배우나 감독의 출연 영화 목록을 반환하는 함수"""
        response = requests.get(
            f'https://api.themoviedb.org/3/person/{person_id}/movie_credits',
            params={
                'api_key': self.api_key,
                'language': 'ko-KR'
            }
        )
        data = response.json()
        return data.get('cast', [])  # 출연 영화 목록 반환
