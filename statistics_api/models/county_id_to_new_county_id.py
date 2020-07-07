from django.db import models

from statistics_api.models.base_model import BaseModel
from statistics_api.models.county import County


class CountyIdToNewCountyId(BaseModel):

    county_id = models.IntegerField(null=False)  # county id
    new_county_id = models.IntegerField(null=False)  # group id

    class Meta:
        db_table = "county_id_to_new_county_id"
        unique_together = (('county', 'new_county_id'), )