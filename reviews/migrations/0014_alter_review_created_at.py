# Generated by Django 5.1.2 on 2024-11-22 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0013_remove_review_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
