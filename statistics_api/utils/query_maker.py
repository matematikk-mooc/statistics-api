import re
from typing import Tuple

from django.core.exceptions import ValidationError

from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory
from statistics_api.models.school import School

SCHOOL_ORGANIZATION_NUMBER = School.organization_number.field.name
GROUP_ORGANIZATION_NUMBER = Group.organization_number.field.name
MEMBERS_COUNT = Group.members_count.field.name
NUMBER_OF_TEACHERS = School.number_of_teachers.field.name
GROUP_TBL_NAME = Group._meta.db_table
GROUP_CATEGORY_TBL_NAME = GroupCategory._meta.db_table
COURSE_OBSERVATION_TBL_NAME = CourseObservation._meta.db_table
SCHOOL_TBL_NAME = School._meta.db_table
GROUP_GROUP_CATEGORY_FK = Group.group_category.field.attname
GROUP_CATEGORY_ID = f"{GROUP_CATEGORY_TBL_NAME}.{GroupCategory._meta.pk.attname}"
GROUP_ID = f"`{GROUP_TBL_NAME}`.{Group._meta.pk.attname}"
SCHOOL_ID = f"`{SCHOOL_TBL_NAME}`.{School._meta.pk.attname}"
COURSE_OBSERVATION_ID = f"`{COURSE_OBSERVATION_TBL_NAME}`.{CourseObservation._meta.pk.attname}"
GROUP_CATEGORY_COURSE_FK = GroupCategory.course.field.attname
GROUP_CATEGORY_CANVAS_ID = f"{GroupCategory._meta.db_table}.{GroupCategory.canvas_id.field.name}"
DATE_RETRIEVED = str(CourseObservation.date_retrieved.field.name)

QUERY_FOR_EMPTY_RESULT = "SELECT NULL LIMIT 0"


def get_org_nrs_str(organization_numbers) -> str:
    if len(organization_numbers) == 0:
        org_nrs_str = "NULL"
    elif len(organization_numbers) == 1:
        org_nrs_str = str(organization_numbers[0])
    else:
        for nr in organization_numbers:
            if not re.match(r"[0-9U][0-9]{8}", str(nr)):
                raise ValidationError("Unexpected format on organization number.")
        org_nrs_str = ', '.join(['\'' + str(i) + '\'' for i in organization_numbers])

    return org_nrs_str


def get_org_nrs_enrollment_counts_and_teacher_counts_query(organization_numbers: Tuple[str], teacher_count_year: int) -> str:
    """
    Returns a prepared SQL statement to retrieve all organization numbers, Canvas enrollment counts (member counts) and
    number of teachers at all schools with specified organization numbers and course_observation ID.
    
    Example statement returned by this function:
    
    SELECT organization_number, SUM(members_count), number_of_teachers FROM `group`
    INNER JOIN group_to_school_relationship ON group_to_school_relationship.group_id = `group`.id
    LEFT JOIN school ON group_to_school_relationship.school_id = `school`.id
    LEFT JOIN group_category ON `group`.group_category_id = group_category.id
    LEFT JOIN course_observation ON group_category.course_id = `course_observation`.id
    WHERE `course_observation`.id = 3
    AND organization_number IN ('975284778', '975284794', '975284786')
    GROUP BY organization_number;
    """

    org_nrs_str = get_org_nrs_str(organization_numbers)

    return f"""SELECT {SCHOOL_TBL_NAME}.{SCHOOL_ORGANIZATION_NUMBER}, SUM({MEMBERS_COUNT}), {NUMBER_OF_TEACHERS} FROM `{GROUP_TBL_NAME}`
    INNER JOIN {SCHOOL_TBL_NAME} ON {SCHOOL_TBL_NAME}.{SCHOOL_ORGANIZATION_NUMBER} = `{GROUP_TBL_NAME}`.{GROUP_ORGANIZATION_NUMBER}
    AND {SCHOOL_TBL_NAME}.{School.year.field.name} = {teacher_count_year}
    LEFT JOIN {GROUP_CATEGORY_TBL_NAME} ON `{GROUP_TBL_NAME}`.{GROUP_GROUP_CATEGORY_FK} = {GROUP_CATEGORY_ID}
    LEFT JOIN {COURSE_OBSERVATION_TBL_NAME} ON {GROUP_CATEGORY_TBL_NAME}.{GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
    WHERE {COURSE_OBSERVATION_ID} = %s
    AND {SCHOOL_TBL_NAME}.{SCHOOL_ORGANIZATION_NUMBER} IN ({org_nrs_str})
    GROUP BY {SCHOOL_TBL_NAME}.{SCHOOL_ORGANIZATION_NUMBER};
    """


def get_org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools_query(
        organization_numbers: Tuple[str], teacher_count_year: int) -> str:
    """
    Returns a prepared SQL statement to retrieve all organization numbers, Canvas enrollment counts (member counts) and
    number of teachers at all schools with specified organization numbers. This query will only return schools
    that are not registered at Canvas, so the Canvas enrollment count will always be 0.
    """

    org_nrs_str = get_org_nrs_str(organization_numbers)

    return f"""SELECT {SCHOOL_ORGANIZATION_NUMBER}, {0}, {NUMBER_OF_TEACHERS} FROM `{SCHOOL_TBL_NAME}`
        WHERE {SCHOOL_ORGANIZATION_NUMBER} IN ({org_nrs_str})
        AND {School.year.field.name} = {teacher_count_year};
        """


def get_org_nrs_and_enrollment_counts_query(organization_numbers: Tuple[str]) -> str:
    """
    Returns a prepared SQL statement to retrieve all organization numbers and Canvas enrollment counts (member counts)
    at all schools with specified organization numbers and course_observation ID.

    Example statement returned by this function:"""

    org_nrs_str = get_org_nrs_str(organization_numbers)

    return f"""SELECT {GROUP_ORGANIZATION_NUMBER}, SUM({MEMBERS_COUNT}) FROM `{GROUP_TBL_NAME}`
        LEFT JOIN {GROUP_CATEGORY_TBL_NAME} ON `{GROUP_TBL_NAME}`.{GROUP_GROUP_CATEGORY_FK} = {GROUP_CATEGORY_ID}
        LEFT JOIN {COURSE_OBSERVATION_TBL_NAME} ON {GROUP_CATEGORY_TBL_NAME}.{GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
        WHERE {COURSE_OBSERVATION_ID} = %s
        AND {GROUP_ORGANIZATION_NUMBER} IN ({org_nrs_str})
        GROUP BY {GROUP_ORGANIZATION_NUMBER};
        """


def get_group_category_observations_between_dates_query() -> str:
    return f"""SELECT {GROUP_CATEGORY_ID}, {DATE_RETRIEVED} FROM {GroupCategory._meta.db_table}
        LEFT JOIN {CourseObservation._meta.db_table} ON {GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
        WHERE {GROUP_CATEGORY_CANVAS_ID} = %s
        AND {DATE_RETRIEVED} >= %s
        AND {DATE_RETRIEVED} <= %s
        ORDER BY {DATE_RETRIEVED} DESC
        LIMIT %s"""


def get_groups_by_group_category_ids_query(group_category_ids: Tuple[int]) -> str:
    if len(group_category_ids) == 0:
        group_category_ids_str = "NULL"
    elif len(group_category_ids) == 1:
        group_category_ids_str = str(group_category_ids[0])
    else:
        group_category_ids_str = ", ".join([str(i) for i in group_category_ids])

    return f"""SELECT `{Group._meta.db_table}`.*, {DATE_RETRIEVED} FROM `{Group._meta.db_table}`
                LEFT JOIN {GroupCategory._meta.db_table} ON {GROUP_GROUP_CATEGORY_FK} = {GROUP_CATEGORY_ID}
                LEFT JOIN {CourseObservation._meta.db_table} ON {GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
                WHERE {GROUP_CATEGORY_ID} IN ({group_category_ids_str})"""


def get_update_group_organization_numbers_query(group_ids_and_org_nrs: Tuple[Tuple[int, str]]) -> str:
    sql_values = []

    for group_id, group_org_nr in group_ids_and_org_nrs:
        sql_values.append(
            f"({group_id}, {0}, '', NULL, {0}, {0}, {0}, {1}, '{group_org_nr}')")

    return f"""INSERT INTO `{GROUP_TBL_NAME}` VALUES\n""" \
           + ", \n".join(sql_values) + \
           f"""\nON DUPLICATE KEY UPDATE {GROUP_ORGANIZATION_NUMBER} = VALUES({GROUP_ORGANIZATION_NUMBER})"""
