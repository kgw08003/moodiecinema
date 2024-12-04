from django.shortcuts import render
from django.views import View
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from jjim.models import Jjim
from collections import Counter
from django.contrib.auth.mixins import LoginRequiredMixin


class MovieSearchView(LoginRequiredMixin, View):
    template_name = 'moodiecinema/search_results.html'
    api_key = '5f0eb3027f1b131897e4dcbe057e0931'

    def get(self, request):
        query = request.GET.get('q')
        page = request.GET.get('page', 1)
        selected_genres = request.GET.getlist('genre')
        actor_name = request.GET.get('actor')
        director_name = request.GET.get('director')
        genres = self.get_genre_list()
        movies = []
        total_pages = 1

        # "추천" 기능: 찜 목록 기반 협업 필터링
        if query == "추천":
            # 세션 캐시 초기화
            if 'reset_cache' in request.GET:
                request.session['cached_movies'] = []
                print("Session cache reset.")  # 디버깅

            # 협업 필터링 추천
            recommended_movie_ids = self.get_recommendations(request.user.pk)
            if recommended_movie_ids:
                movies = self.get_movie_details(recommended_movie_ids, request.user.pk)
            else:
                movies = []  # 추천 데이터가 없는 경우 빈 결과 반환

        # 일반 검색 기능
        elif query:
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

            # 영화 검색 결과가 없으면 배우/감독으로 검색
            if not movies:
                movies = self.search_by_person(query, page)

        # 필터 기반 검색 (장르, 배우, 감독)
        elif selected_genres or actor_name or director_name:
            movies, total_pages = self.search_by_filters(selected_genres, actor_name, director_name, page)

        # 캐싱 데이터로 중복 방지 및 로테이션
        cached_movies = request.session.get('cached_movies', [])
        movies = self.rotate_recommendations(movies, cached_movies)
        request.session['cached_movies'] = [movie['id'] for movie in movies]

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
        """TMDb API에서 장르 목록 가져오기"""
        response = requests.get(
            'https://api.themoviedb.org/3/genre/movie/list',
            params={'api_key': self.api_key, 'language': 'ko-KR'}
        )
        data = response.json()
        return data.get('genres', [])

    def search_by_person(self, query, page):
        """배우 또는 감독으로 영화 검색"""
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
        movies = []

        if people:
            for person in people:
                known_for_movies = person.get('known_for', [])
                full_movie_credits = self.get_movie_credits(person['id'])
                for movie in known_for_movies + full_movie_credits:
                    if movie not in movies:
                        movies.append(movie)

        return movies

    def search_by_filters(self, selected_genres, actor_name, director_name, page):
        """장르, 배우, 감독 필터 기반 영화 검색"""
        actor_id = self.get_person_id(actor_name) if actor_name else None
        director_id = self.get_person_id(director_name) if director_name else None
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
        return data.get('results', []), data.get('total_pages', 1)

    def rotate_recommendations(self, movies, cached_movies):
        """중복 방지를 위한 캐싱 처리"""
        unique_movies = [movie for movie in movies if movie['id'] not in cached_movies]
        if not unique_movies:
            return movies[:10]  # 캐싱된 영화만 있으면 일부 반환
        return unique_movies[:10]

    def get_person_id(self, name):
        """배우 또는 감독 이름으로 ID 가져오기"""
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
            return None
        return person[0]['id']

    def get_movie_credits(self, person_id):
        """특정 배우나 감독의 영화 목록 가져오기"""
        response = requests.get(
            f'https://api.themoviedb.org/3/person/{person_id}/movie_credits',
            params={
                'api_key': self.api_key,
                'language': 'ko-KR'
            }
        )
        data = response.json()
        return data.get('cast', [])
    
    def get_recommendations(self, user_id):
        """찜 목록 기반 협업 필터링 추천"""
        # 사용자 찜 목록 가져오기
        user_jjims = list(Jjim.objects.filter(user_id=user_id).values_list('movie_id', flat=True))
        print(f"Updated Jjim List for User {user_id}: {user_jjims}")  # 디버깅

        if not user_jjims:
            return []

        # 모든 사용자-영화 데이터 가져오기
        data = Jjim.objects.values('user_id', 'movie_id')
        df = pd.DataFrame(data)
        if df.empty:
            return []

        # 사용자-영화 매트릭스 생성
        user_item_matrix = df.pivot_table(index='user_id', columns='movie_id', aggfunc='size', fill_value=0)
        print(f"User-Item Matrix:\n{user_item_matrix}")  # 디버깅

        # 유사도 계산
        similarity_matrix = cosine_similarity(user_item_matrix)
        similarity_df = pd.DataFrame(similarity_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)
        print(f"Similarity Matrix:\n{similarity_df}")  # 디버깅

        # 유사 사용자 추출
        similar_users = similarity_df[user_id].sort_values(ascending=False)
        print(f"Similar Users:\n{similar_users}")  # 디버깅

        # 현재 사용자가 보지 않은 영화 추출
        user_movies = user_item_matrix.loc[user_id]
        unseen_movies = user_item_matrix.columns[user_movies == 0]
        if unseen_movies.empty:
            return []

        # 가중치 계산
        weighted_scores = user_item_matrix.loc[similar_users.index, unseen_movies].T.dot(similar_users)
        print(f"Weighted Scores:\n{weighted_scores}")  # 디버깅

        # 장르 가중치 추가
        genre_weights = pd.Series({movie_id: sum(1 for g in self.get_movie_genres(movie_id)) for movie_id in unseen_movies})
        print(f"Genre Weights:\n{genre_weights}")  # 디버깅

        # 최종 점수 계산
        final_scores = weighted_scores + genre_weights
        print(f"Final Scores:\n{final_scores}")  # 디버깅

        # 추천 영화 ID 반환
        recommended_movie_ids = final_scores.sort_values(ascending=False).head(20).index
        print(f"Recommended Movie IDs: {list(recommended_movie_ids)}")  # 디버깅

        return [movie_id for movie_id in recommended_movie_ids if movie_id not in user_jjims][:10]
        
    def get_movie_genres(self, movie_id):
        """특정 영화의 장르 ID 가져오기"""
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}',
            params={'api_key': self.api_key, 'language': 'ko-KR'}
        )
        if response.status_code == 200:
            movie_data = response.json()
            return [genre['id'] for genre in movie_data.get('genres', [])]
        return []

    def get_movie_details(self, movie_ids, user_id):
        """TMDb API에서 영화 상세 정보 가져오기"""
        movie_details = []
        all_genres = []

        for movie_id in movie_ids:
            response = requests.get(
                f'https://api.themoviedb.org/3/movie/{movie_id}',
                params={'api_key': self.api_key, 'language': 'ko-KR'}
            )
            if response.status_code == 200:
                movie_data = response.json()
                movie_details.append(movie_data)
                genres = movie_data.get('genres', [])
                all_genres.extend([genre['id'] for genre in genres])

        if len(movie_details) < 10:
            genre_counter = Counter(all_genres)
            most_common_genres = [genre[0] for genre in genre_counter.most_common(3)]
            additional_movies = self.get_movies_by_genres(most_common_genres, 10 - len(movie_details), movie_ids)
            movie_details.extend(additional_movies)

        return movie_details

    def get_movies_by_genres(self, genre_ids, count, exclude_movie_ids):
        """특정 장르의 영화 가져오기"""
        genre_ids_str = ','.join(map(str, genre_ids))
        response = requests.get(
            'https://api.themoviedb.org/3/discover/movie',
            params={
                'api_key': self.api_key,
                'language': 'ko-KR',
                'with_genres': genre_ids_str,
                'sort_by': 'popularity.desc',
                'page': 1
            }
        )
        data = response.json()
        movies = data.get('results', [])
        return [movie for movie in movies if movie['id'] not in exclude_movie_ids][:count]
