# Generated by Django 5.1.2 on 2024-11-14 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_rename_sentiment_review_emotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='is_reported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='review',
            name='reported_count',
            field=models.IntegerField(default=0),
        ),
    ]