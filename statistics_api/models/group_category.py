from django.db import models

from statistics_api.definitions import MYSQL_VARCHAR_DEFAULT_LENGTH
from statistics_api.models.base_model import BaseModel
from statistics_api.models.course import Course


class GroupCategory(BaseModel):
    name = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH)
    canvas_id = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # course_id

    class Meta:
        db_table = "group_category"
