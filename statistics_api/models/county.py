from django.db import models
from statistics_api.models.base_model import BaseModel

class County(BaseModel):

    county_id = models.IntegerField(unique=True)

    number_of_teachers = models.IntegerField()
    updated_date = models.DateTimeField()

    class Meta:
        db_table = "county"