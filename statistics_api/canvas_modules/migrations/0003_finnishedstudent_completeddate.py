# Generated by Django 3.2.13 on 2023-03-27 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvas_modules', '0002_auto_20221101_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='finnishedstudent',
            name='completedDate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
