from django.db import models

# Create your models here.

class QuizStatistics(models.Model):
    canvas_quiz_id = models.CharField(max_length=10)
    canvas_course_id = models.CharField(max_length=10)
    canvas_id = models.CharField(
        max_length=80)

class QuestionStatistics(models.Model):
    canvas_id = models.CharField(max_length=80)
    question_type = models.CharField(max_length=80)
    question_text= models.CharField(max_length=255)
    responses = models.IntegerField()
    quiz_statistics = models.ForeignKey(QuizStatistics, on_delete=models.CASCADE)

class Answer(models.Model):
    canvas_id = models.CharField(
        max_length=80)
    text = models.CharField(
        max_length=255)
    responses = models.IntegerField()
    question_statistics = models.ForeignKey(QuestionStatistics, on_delete=models.CASCADE)

class SubmissionStatistics(models.Model):
    unique_count = models.IntegerField()
    quiz_statistics = models.ForeignKey(QuizStatistics, on_delete=models.CASCADE)
