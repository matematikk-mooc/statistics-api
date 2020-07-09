from datetime import datetime
from typing import List, Dict, Tuple, Union

from django.db import connection

from statistics_api.models.county import County
from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory
from statistics_api.models.school import School


def get_is_school_and_org_nr(group_description: str) -> Tuple[bool, str]:
    _, _, institution_type, _, organization_number = ([s.strip() for s in group_description.split(":")] + [""]*5)[:5]
    return institution_type.strip().lower() == "school", organization_number


class DatabaseClient:

    pass
