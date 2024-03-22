from django.db import models
from itertools import chain

from statistics_api.definitions import MYSQL_VARCHAR_DEFAULT_LENGTH

# Create your models here.

class BaseModel(models.Model):

    objects = models.Manager()

    def to_dict(instance):
        opts = instance._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.attname] = f.value_from_object(instance)
        for f in opts.many_to_many:
            data[f.attname] = [i.id for i in f.value_from_object(instance)]
        return data

    class Meta:
        abstract = True


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


class CourseObservation(BaseModel):

    date_retrieved = models.DateTimeField(auto_now_add=True, db_index=True)
    canvas_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH)

    class Meta:
        db_table = "course_observation"


class GroupCategory(BaseModel):

    name = models.CharField(max_length=MYSQL_VARCHAR_DEFAULT_LENGTH)
    canvas_id = models.IntegerField(db_index=True)
    course = models.ForeignKey(CourseObservation, on_delete=models.CASCADE)  # course_id

    class Meta:
        db_table = "group_category"


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
        db_table = "group"



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
