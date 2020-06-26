import logging
import sys
from typing import Dict, List

from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.clients.db_client import DatabaseClient
from statistics_api.models.group_to_school_relationship import GroupToSchoolRelationship
from statistics_api.models.school import School


class Command(BaseCommand):
    help = """Accesses API of environment configured Canvas LMS instance and pulls member counts from all groups 
    associated with all courses associated with the root account ID in environment configuration."""

    @transaction.atomic
    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()

        api_client = CanvasApiClient()
        db_client = DatabaseClient()

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

        all_groups: List[Dict] = []

        for group_category in all_group_categories:
            groups_for_course = api_client.get_groups_by_group_category_id(group_category['id'])
            for group in groups_for_course:
                group['group_category_id'] = group_category['db_id']

            all_groups += groups_for_course

        all_db_groups = db_client.insert_groups(tuple(all_groups))

        logger.info(f"Inserted {len(all_db_groups)} groups")

        group_to_school_relationships = []

        for db_group, group in zip(all_db_groups, all_groups):
            _, _, institution_type, _, organization_number = [s.strip() for s in group['description'].split(":")]
            if institution_type.lower().strip() == "school":
                schools = School.objects.filter(organization_number=organization_number)
                if len(schools) == 0:
                    continue
                elif len(schools) == 1:
                    pass
                else:
                    raise AssertionError(f"More than 1 school has organization number {organization_number}")
                group_to_school_relationship = GroupToSchoolRelationship(school=schools[0], group=db_group)
                group_to_school_relationships.append(group_to_school_relationship)

        GroupToSchoolRelationship.objects.bulk_create(group_to_school_relationships)

        logger.info(
            f"Mapped {len(group_to_school_relationships)} out of {len(all_db_groups)} groups to known schools from NSR.")
