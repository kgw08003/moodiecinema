# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, user_name, user_email, user_password=None, **extra_fields):
        if not user_email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(user_email)
        user = self.model(user_name=user_name, user_email=email, **extra_fields)
        user.set_password(user_password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, user_email, user_password=None, **extra_fields):
        extra_fields.setdefault('admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(user_name, user_email, user_password, **extra_fields)

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50, unique=True)
    user_password = models.CharField(max_length=128)
    user_profile = models.ImageField(upload_to='profiles/', null=True, blank=True)
    user_email = models.EmailField(unique=True)
    user_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True) 
    admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # 추가된 필드
    is_superuser = models.BooleanField(default=False)  # 추가된 필드

    objects = UserManager()

    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['user_email']

    def __str__(self):
        return self.user_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


from django.db import models
from django.conf import settings

class Diary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diaries")
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateField() 
    emotion = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.title