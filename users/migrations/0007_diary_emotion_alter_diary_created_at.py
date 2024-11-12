# Generated by Django 5.1.2 on 2024-11-08 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_diary_emotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='emotion',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='diary',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
