# Generated by Django 5.1.2 on 2024-11-18 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0010_reviewreport_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewreport',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
