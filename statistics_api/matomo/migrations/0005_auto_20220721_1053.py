# Generated by Django 3.2.13 on 2022-07-21 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matomo', '0004_alter_pagestatistics_segment'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagestatistics',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subpages', to='matomo.pagestatistics'),
        ),
        migrations.AlterField(
            model_name='pagestatistics',
            name='average_time_spent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
