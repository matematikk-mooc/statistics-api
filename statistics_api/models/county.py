from django.db import models
from statistics_api.models.base_model import BaseModel

class County(BaseModel):

    county_id = models.IntegerField()

    number_of_teachers = models.IntegerField()
    updated_date = models.DateTimeField()

    # Number of high school teachers per county data are imported from reports from Skoleporten.
    # This field is the year of the report. If the data is from e.g. 2019-2020, this field should
    # be the 'start year', 2019
    year = models.IntegerField()

    class Meta:
        db_table = "county"
        unique_together = (('county_id', 'year'),)