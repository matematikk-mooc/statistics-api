# Generated by Django 3.2.13 on 2022-07-22 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matomo', '0005_auto_20220721_1053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagestatistics',
            name='parent',
        ),
        migrations.AddField(
            model_name='pagestatistics',
            name='canvas_course_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]