from typing import Tuple

from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory
from statistics_api.models.group_to_school_relationship import GroupToSchoolRelationship
from statistics_api.models.school import School

ORGANIZATION_NUMBER = School.organization_number.field.name
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
GROUP_TO_SCHOOL_RELATIONSHIP_TBL_NAME = GroupToSchoolRelationship._meta.db_table
GROUP_TO_SCHOOL_RELATIONSHIP_GROUP_FK = GroupToSchoolRelationship.group.field.attname
GROUP_TO_SCHOOL_RELATIONSHIP_SCHOOL_FK = GroupToSchoolRelationship.school.field.attname
GROUP_CATEGORY_COURSE_FK = GroupCategory.course.field.attname


def get_org_nrs_enrollment_counts_and_teacher_counts_query(organization_numbers: Tuple[int]) -> str:
    """
    Returns a prepared SQL statement to retrieve all organization numbers, Canvas enrollment counts (member counts) and
    number of teachers at all primary schools within a municipality specified by a municipality ID and a course_observation ID.
    
    Example statement returned by this method:
    
    SELECT organization_number, members_count, number_of_teachers FROM `group`
    LEFT JOIN group_category ON `group`.group_category_id = group_category.id
    INNER JOIN group_to_school_relationship ON group_to_school_relationship.group_id = `group`.id
    LEFT JOIN course_observation ON group_category.course_id = course_observation.id
    LEFT JOIN school ON group_to_school_relationship.school_id = school.id
    WHERE course_observation.id = %s
    AND organization_number IN ('987654321', '987654320', '987654319', '987654318');
    """

    org_nrs_str = ', '.join(['\'' + str(i) + '\'' for i in organization_numbers]) if organization_numbers else "''"

    return f"""SELECT {ORGANIZATION_NUMBER}, {MEMBERS_COUNT}, {NUMBER_OF_TEACHERS} FROM `{GROUP_TBL_NAME}`
    LEFT JOIN {GROUP_CATEGORY_TBL_NAME} ON `{GROUP_TBL_NAME}`.{GROUP_GROUP_CATEGORY_FK} = {GROUP_CATEGORY_ID}
    INNER JOIN {GROUP_TO_SCHOOL_RELATIONSHIP_TBL_NAME} ON {GROUP_TO_SCHOOL_RELATIONSHIP_TBL_NAME}.{GROUP_TO_SCHOOL_RELATIONSHIP_GROUP_FK} = {GROUP_ID}
    LEFT JOIN {COURSE_OBSERVATION_TBL_NAME} ON {GROUP_CATEGORY_TBL_NAME}.{GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
    LEFT JOIN {SCHOOL_TBL_NAME} ON {GROUP_TO_SCHOOL_RELATIONSHIP_TBL_NAME}.{GROUP_TO_SCHOOL_RELATIONSHIP_SCHOOL_FK} = {SCHOOL_ID}
    WHERE {COURSE_OBSERVATION_ID} = %s
    AND {ORGANIZATION_NUMBER} IN ({org_nrs_str});
    """
