from datetime import datetime

from django.db import models

from statistics_api.definitions import MYSQL_VARCHAR_DEFAULT_LENGTH
from statistics_api.models.base_model import BaseModel


class CourseObservation(BaseModel):

    date_retrieved = models.DateTimeField(auto_now_add=True)
    canvas_id = models.IntegerField()
    name = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH)

    class Meta:
        db_table = "course_observation"
