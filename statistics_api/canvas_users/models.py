from django.db import models

# Create your models here.

class CanvasUser(models.Model):
    canvas_user_id = models.CharField(max_length=10)
    course_id = models.CharField(max_length=10)
    group_id = models.CharField(max_length=10)
    group_name = models.CharField(max_length=255)
    group_description = models.CharField(max_length=255, null=True, blank=True)

class Meta:
    db_table = "canvas_user"