# Generated by Django 3.2.13 on 2022-07-19 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_remove_submissionstatistics_canvas_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizstatistics',
            name='title',
            field=models.CharField(default='', max_length=512),
        ),
    ]