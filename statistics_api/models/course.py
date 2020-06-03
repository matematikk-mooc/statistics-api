from django.db import models

from statistics_api.definitions import MYSQL_VARCHAR_DEFAULT_LENGTH
from statistics_api.models.base_model import BaseModel


class Course(BaseModel):
    canvas_id = models.IntegerField()
    name = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH)
    total_nr_of_students = models.IntegerField()

    class Meta:
        db_table = "course"
