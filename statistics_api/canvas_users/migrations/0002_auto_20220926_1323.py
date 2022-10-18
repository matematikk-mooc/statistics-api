# Generated by Django 3.2.13 on 2022-09-26 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvas_users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='canvasuser',
            name='course_id',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='canvasuser',
            name='group_description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
