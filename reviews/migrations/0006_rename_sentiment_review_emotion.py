# Generated by Django 5.1.2 on 2024-11-13 02:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_review_sentiment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='sentiment',
            new_name='emotion',
        ),
    ]