from django.db import models

from statistics_api.definitions import MYSQL_VARCHAR_DEFAULT_LENGTH
from statistics_api.models.base_model import BaseModel
from statistics_api.models.group_category import GroupCategory


class Group(BaseModel):
    canvas_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH)
    group_category = models.ForeignKey(GroupCategory, on_delete=models.CASCADE)  # group_category id
    description = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH, null=True, blank=True, default=None)
    organization_number = models.CharField(max_length=9, null=True, db_index=True)
    created_at = models.DateTimeField()
    updated_date = models.DateTimeField(auto_now=True)
    members_count = models.IntegerField()
    aggregated = models.BooleanField(default=False)

    class Meta:
        db_table = "canvas_group"
