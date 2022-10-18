from django.db import models

# Create your models here.

class QuizStatistics(models.Model):
    canvas_quiz_id = models.CharField(max_length=10)
    canvas_course_id = models.CharField(max_length=10)
    canvas_id = models.CharField(max_length=80)
    title = models.CharField(max_length=512, default="")

class QuestionStatistics(models.Model):
    canvas_id = models.CharField(max_length=80)
    question_type = models.CharField(max_length=80)
    question_text= models.CharField(max_length=1024)
    responses = models.IntegerField(blank=True, null=True)
    quiz_statistics = models.ForeignKey(QuizStatistics, on_delete=models.CASCADE, related_name="question_statistics")

class AnswerSet(models.Model):
    canvas_id = models.CharField(max_length=80)
    text = models.CharField(max_length=512)
    question_statistics = models.ForeignKey(QuestionStatistics, on_delete=models.CASCADE, related_name="answer_sets", blank=True, null=True)

class Answer(models.Model):
    canvas_id = models.CharField(max_length=80)
    text = models.CharField(max_length=512, blank=True, null=True)
    responses = models.IntegerField()
    question_statistics = models.ForeignKey(QuestionStatistics, on_delete=models.CASCADE, related_name="answers", blank=True, null=True)
    answer_sets = models.ForeignKey(AnswerSet, on_delete=models.CASCADE, related_name="answers", blank=True, null=True)

class AnswerUserGroup(models.Model):
    group_name = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.CharField(max_length=80)
    count = models.IntegerField()
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="user_groups", blank=True, null=True)

#class OpenAnswerResponse(models.Model):
#    answer = models.CharField(max_length=512)
#    question_statistics = models.ForeignKey(QuestionStatistics, on_delete=models.CASCADE, related_name="open_responses", blank=True, null=True)

class SubmissionStatistics(models.Model):
    unique_count = models.IntegerField()
    quiz_statistics = models.ForeignKey(QuizStatistics, on_delete=models.CASCADE, related_name="submission_statistics")
