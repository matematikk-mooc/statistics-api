# Generated by Django 3.0.7 on 2020-06-25 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics_api', '0009_auto_20200625_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='organization_number',
            field=models.CharField(max_length=9, unique=True),
        ),
    ]
