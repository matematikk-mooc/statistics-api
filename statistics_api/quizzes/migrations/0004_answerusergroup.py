# Generated by Django 3.2.13 on 2022-10-07 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0003_quizstatistics_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerUserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(blank=True, max_length=255, null=True)),
                ('group_id', models.CharField(max_length=80)),
                ('count', models.IntegerField()),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_groups', to='quizzes.answer')),
            ],
        ),
    ]