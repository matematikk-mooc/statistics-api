# Generated by Django 3.2.11 on 2022-01-24 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment_activity', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollmentactivity',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
