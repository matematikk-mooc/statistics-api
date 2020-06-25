from django.db import models
from statistics_api.models.base_model import BaseModel

class School(BaseModel):

    # organization IDs may belong to foreign institutions with non-numeric IDs
    organization_number = models.CharField(max_length=9, unique=True)

    number_of_teachers = models.IntegerField()
    updated_date = models.DateTimeField()

    class Meta:
        db_table = "school"