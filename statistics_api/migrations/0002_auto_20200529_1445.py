# Generated by Django 3.0.6 on 2020-05-29 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
