from django.db import models


class EnrollmentActivity(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.IntegerField()
    course_name = models.CharField(
        max_length=80,
        help_text="Name of the course")
    active_users_count = models.IntegerField()
    activity_date = models.DateTimeField(
        auto_now_add=False,
        auto_now=False, )
    created_at = models.DateTimeField(
        auto_now_add=True,
        auto_now=False, )
