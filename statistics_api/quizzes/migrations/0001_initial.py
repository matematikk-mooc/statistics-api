# Generated by Django 3.2.13 on 2022-06-22 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QuizStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canvas_quiz_id', models.CharField(max_length=10)),
                ('canvas_course_id', models.CharField(max_length=10)),
                ('canvas_id', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canvas_id', models.CharField(max_length=80)),
                ('unique_count', models.IntegerField()),
                ('quiz_statistics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_statistics', to='quizzes.quizstatistics')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canvas_id', models.CharField(max_length=80)),
                ('question_type', models.CharField(max_length=80)),
                ('question_text', models.CharField(max_length=1024)),
                ('responses', models.IntegerField(blank=True, null=True)),
                ('quiz_statistics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_statistics', to='quizzes.quizstatistics')),
            ],
        ),
        migrations.CreateModel(
            name='AnswerSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canvas_id', models.CharField(max_length=80)),
                ('text', models.CharField(max_length=512)),
                ('question_statistics', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_sets', to='quizzes.questionstatistics')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canvas_id', models.CharField(max_length=80)),
                ('text', models.CharField(blank=True, max_length=512, null=True)),
                ('responses', models.IntegerField()),
                ('answer_sets', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizzes.answerset')),
                ('question_statistics', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizzes.questionstatistics')),
            ],
        ),
    ]
