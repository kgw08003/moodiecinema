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