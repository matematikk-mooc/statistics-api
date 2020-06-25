from django.db import models

from statistics_api.models.base_model import BaseModel
from statistics_api.models.group import Group
from statistics_api.models.school import School


class GroupToSchoolRelationship(BaseModel):

    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # group id
    school = models.ForeignKey(School, on_delete=models.CASCADE)  # group id

    class Meta:
        db_table = "group_to_school_relationship"
        unique_together = (('group', 'school'), )