from django.db import models

# Create your models here.
class TotalStudents(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    course_id = models.CharField(max_length=10)
    total_students = models.IntegerField()

    class Meta:
        db_table = "total_students"