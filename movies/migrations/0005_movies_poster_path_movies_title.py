# Generated by Django 5.1.2 on 2024-11-11 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_remove_movies_poster_path_remove_movies_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='movies',
            name='poster_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='movies',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
