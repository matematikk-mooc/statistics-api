from django.db import models

# Create your models here.

class Visits(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    visits = models.IntegerField(null=True, blank=True)
    unique_visitors = models.IntegerField(null=True, blank=True)
    unique_visitors_new = models.IntegerField(null=True, blank=True)
    unique_visitors_returning = models.IntegerField(null=True, blank=True)
    visits_new = models.IntegerField(null=True, blank=True)
    visits_returning = models.IntegerField(null=True, blank=True)
    bounce_count_new = models.IntegerField(null=True, blank=True)
    bounce_count_returning = models.IntegerField(null=True, blank=True)
    sum_visit_length_new = models.IntegerField(null=True, blank=True)
    sum_visit_length_returning = models.IntegerField(null=True, blank=True)
    actions_new = models.IntegerField(null=True, blank=True)
    actions_returning = models.IntegerField(null=True, blank=True)
    max_actions_new = models.IntegerField(null=True, blank=True)
    max_actions_returning = models.IntegerField(null=True, blank=True)
    bounce_rate_new = models.CharField(max_length=10, null=True, blank=True)
    bounce_rate_returning = models.CharField(max_length=10, null=True, blank=True)
    avg_time_on_site_new = models.IntegerField(null=True, blank=True)
    avg_time_on_site_returning = models.IntegerField(null=True, blank=True)
    actions_per_visit_new = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    actions_per_visit_returning = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)


class PageStatistics(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    canvas_course_id = models.CharField(max_length=10, null=True, blank=True)
    label = models.CharField(max_length=255)
    visits = models.IntegerField(null=True, blank=True)
    sum_time_spent = models.IntegerField(null=True, blank=True)
    average_time_spent = models.IntegerField(null=True, blank=True)
    unique_visitors = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=1024, null=True, blank=True)
    bounce_rate = models.CharField(max_length=10, null=True, blank=True)
    exit_rate = models.CharField(max_length=10, null=True, blank=True)
    exit_visits = models.IntegerField(null=True, blank=True)
    entry_visits = models.IntegerField(null=True, blank=True)
    segment = models.CharField(max_length=512, null=True, blank=True)
