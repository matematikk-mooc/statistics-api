from django.db import models
from statistics_api.models.base_model import BaseModel


class School(BaseModel):

    # organization IDs may belong to foreign institutions with non-numeric IDs
    organization_number = models.CharField(max_length=9)

    number_of_teachers = models.IntegerField(null=True)
    updated_date = models.DateTimeField()

    # Number of primary school teachers per school data are imported from reports from Skoleporten.
    # This field is the year of the report. If the data is from e.g. 2019-2020, this field should
    # be the 'start year', 2019
    year = models.IntegerField()

    class Meta:
        db_table = "school"
        unique_together = (('organization_number', 'year'),)
