# Generated by Django 3.2.13 on 2022-07-21 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matomo', '0002_pagestatistics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagestatistics',
            name='url',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
