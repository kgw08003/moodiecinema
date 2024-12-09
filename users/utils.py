from .models import User

def save_user_details(backend, uid, user=None, response=None, *args, **kwargs):
    if user is None:
        email = response.get('response', {}).get('email')
        name = response.get('response', {}).get('name')  # 회원 이름
        nickname = response.get('response', {}).get('nickname')  # 별명

        # 이메일이 없는 경우 기본 이메일 설정
        if not email:
            email = f"{uid}@example.com"

        # user_name이 없는 경우, 회원 이름(name) 또는 별명(nickname)으로 설정
        username = name if name else nickname

        # 회원 이름과 별명 모두 없는 경우 UID 일부 사용
        if not username:
            username = uid[:5]

        user = User.objects.create_user(user_name=username, user_email=email)
    return {'user': user}
