# moodiecinema/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'moodiecinema/home.html')

