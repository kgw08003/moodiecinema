# Generated by Django 5.1.2 on 2024-11-11 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_movies_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movies',
            name='poster_path',
        ),
        migrations.RemoveField(
            model_name='movies',
            name='title',
        ),
    ]
