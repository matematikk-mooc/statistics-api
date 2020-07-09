import logging
import sys
from typing import Dict, List

from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.clients.db_maintenance_client import DatabaseMaintenanceClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID


class Command(BaseCommand):
    help = """Accesses API of environment configured Canvas LMS instance and pulls member counts from all groups 
    associated with all courses associated with the root account ID in environment configuration."""

    @transaction.atomic
    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()

        api_client = CanvasApiClient()

        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id=canvas_account_id)
        courses = DatabaseMaintenanceClient.insert_courses(courses)
        logger.info(f"Inserted {len(courses)} courses")

        all_group_categories = []

        for course in courses:
            group_categories_for_course = api_client.get_group_categories_by_course(course['id'])
            for group_category in group_categories_for_course:
                group_category['course_id'] = course['db_id']

            all_group_categories += group_categories_for_course

        all_group_categories = DatabaseMaintenanceClient.insert_group_categories(all_group_categories)
        logger.info(f"Inserted {len(all_group_categories)} group categories")

        all_groups: List[Dict] = []

        for group_category in all_group_categories:
            groups_for_course = api_client.get_groups_by_group_category_id(group_category['id'])
            for group in groups_for_course:
                group['group_category_id'] = group_category['db_id']

            all_groups += groups_for_course

        all_db_groups = DatabaseMaintenanceClient.insert_groups(tuple(all_groups))

        logger.info(f"Inserted {len(all_db_groups)} groups")
