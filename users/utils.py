# users/utils.py
from .models import User

def save_user_details(backend, uid, user=None, response=None, *args, **kwargs):
    if user is None:
        email = response.get('email')
        username = response.get('name')
        user = User.objects.create_user(user_name=username, user_email=email)
    return {'user': user}