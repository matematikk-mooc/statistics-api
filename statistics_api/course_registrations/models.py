from django.db import models

# Create your models here.

class DailyRegistrations(models.Model):
    course_id = models.IntegerField()
    group_id = models.IntegerField(null=True, blank=True)
    group_name = models.CharField(max_length=512, null=True, blank=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    registrations = models.IntegerField()

    class Meta:
        db_table = "daily_registrations"
