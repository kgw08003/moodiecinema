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
        return self.create_user(user_name, user_email, user_password, **extra_fields)

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50, unique=True)
    user_password = models.CharField(max_length=128)  # Will be handled by Django's set_password method
    user_profile = models.ImageField(upload_to='profiles/', null=True, blank=True)
    user_email = models.EmailField(unique=True)
    user_birth = models.DateField(null=True, blank=True)
    admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.user_name

    @property
    def is_staff(self):
        return self.admin

    @property
    def is_superuser(self):
        return self.admin
