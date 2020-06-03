import logging
import sys

from statistics_api.api_client import ApiClient
from statistics_api.db_client import DatabaseClient
from statistics_api.models.course import Course
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory
from django.db import transaction


@transaction.atomic
def refresh_database():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger = logging.getLogger()

    api_client = ApiClient()
    db_client = DatabaseClient()

    for existing_table in [Course.objects.all(), GroupCategory.objects.all(), Group.objects.all()]:
        existing_table.delete()

    logger.info("Truncated database")

    courses = api_client.get_courses()
    courses = db_client.insert_courses(courses)
    logger.info(f"Inserted {len(courses)} courses")

    all_group_categories = []

    for course in courses:
        group_categories_for_course = api_client.get_group_categories_by_course(course['id'])
        for group_category in group_categories_for_course:
            group_category['course_id'] = course['db_id']

        all_group_categories += group_categories_for_course

    all_group_categories = db_client.insert_group_categories(all_group_categories)
    logger.info(f"Inserted {len(all_group_categories)} group categories")

    all_groups = []

    for group_category in all_group_categories:
        groups_for_course = api_client.get_groups_by_group_category_id(group_category['id'])
        for group in groups_for_course:
            group['group_category_id'] = group_category['db_id']

        all_groups += groups_for_course

    db_client.insert_groups(all_groups)
    logger.info(f"Inserted {len(all_groups)} groups")
