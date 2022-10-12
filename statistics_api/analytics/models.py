from statistics import mode
from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class CanvasAnalytics(models.Model):
    course_id = models.CharField(max_length=80)
    date = models.DateField()
    views = models.IntegerField()
    participations = models.IntegerField()

class Meta:
    db_table = "canvas_analytics"
