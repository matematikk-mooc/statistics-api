from django.db import models

from statistics_api.definitions import MYSQL_VARCHAR_DEFAULT_LENGTH, STRFTIME_FORMAT
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

    def to_dict(instance):
        return {
            "id": instance.pk,
            "canvas_id": instance.canvas_id,
            "category_id": instance.group_category.pk,
            "name": instance.name,
            "description": instance.description,
            "created_at": instance.created_at.strftime(STRFTIME_FORMAT),
            "updated_at": instance.updated_date.strftime(STRFTIME_FORMAT),
            "members_count": instance.members_count
        }

    class Meta:
        db_table = "group"
