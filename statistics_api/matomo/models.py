from django.db import models

# Create your models here.

class Visits(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    visits = models.IntegerField()
    unique_visitors = models.IntegerField()

class PageStatistics(models.Model): 
    date = models.DateField(auto_now=False, auto_now_add=False)
    canvas_course_id = models.CharField(max_length=10, null=True, blank=True)
    label = models.CharField(max_length=255)
    visits = models.IntegerField(null=True, blank=True)
    sum_time_spent = models.IntegerField(null=True, blank=True)
    average_time_spent = models.IntegerField(null=True, blank=True)
    unique_visitors = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=512, null=True, blank=True)
    bounce_rate = models.CharField(max_length=10, null=True, blank=True)
    exit_rate = models.CharField(max_length=10, null=True, blank=True)
    exit_visits = models.IntegerField(null=True, blank=True)
    entry_visits = models.IntegerField(null=True, blank=True)
    segment = models.CharField(max_length=512)
