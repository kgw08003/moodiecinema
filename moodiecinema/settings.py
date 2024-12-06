"""
Django settings for moodiecinema project.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i^4dg$lv4d%)&wkni$y$*ici3ki8t_b3j#hvjd-w7s#&!2653&'
# SECRET_KEY = os.getenv('SECRET_KEY') # 이걸로 배포시 수정 .env에 추가

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWD_HOST = ['*']

AUTH_USER_MODEL = 'users.User'

LOGIN_REDIRECT_URL = 'home'  # 로그인 후 이동할 URL의 name
LOGOUT_REDIRECT_URL = '/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'django.contrib.sites',  
    'social_django',  # social_django 추가
    'diary',
    'movies',
    'reviews',
    'rest_framework',
    'genres',
    'jjim',
    'user_profile',
    'chatbot',
    'community',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'moodiecinema.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # BASE_DIR 하위의 templates 폴더 설정
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', 
                'django.template.context_processors.media', 
            ],
        },
    },
]

WSGI_APPLICATION = 'moodiecinema.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # static 폴더를 지정

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # 구글 소셜 로그인 백엔드 추가
    'django.contrib.auth.backends.ModelBackend',  # 기본 백엔드
    'social_core.backends.naver.NaverOAuth2', # 네이버 소셜 로그인 백엔드 추가
    'social_core.backends.kakao.KakaoOAuth2',    # 카카오 소셜 로그인 백엔드
)

from decouple import config

# Social Auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = config('SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI')
SOCIAL_AUTH_NAVER_KEY = config('SOCIAL_AUTH_NAVER_KEY')
SOCIAL_AUTH_NAVER_SECRET = config('SOCIAL_AUTH_NAVER_SECRET')
SOCIAL_AUTH_NAVER_REDIRECT_URI = 'http://127.0.0.1:8000/auth/complete/naver/'
SOCIAL_AUTH_KAKAO_KEY = config('SOCIAL_AUTH_KAKAO_KEY')
SOCIAL_AUTH_KAKAO_REDIRECT_URI = 'http://127.0.0.1:8000/auth/complete/kakao/'


# Social Auth Pipeline
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'users.utils.save_user_details',  # 커스텀 사용자 저장 함수
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',  # HTML 렌더링 추가
    ),
}
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

import os
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

# 아이디 비밀번호 찾기
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # 기본 설정
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

# 스포티파이 api
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# TMDB api
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

# 허깅페이스 api (올라마 대용)
BASE_DIR = Path(__file__).resolve().parent.parent
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
