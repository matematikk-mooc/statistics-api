import logging
import sys
from typing import Dict, List, Tuple

from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.course_info.models import CourseObservation
from statistics_api.course_info.models import Group
from statistics_api.course_info.models import GroupCategory
from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from statistics_api.course_info.utils import Utils


class Command(BaseCommand):
    help = """Accesses API of environment configured Canvas LMS instance and pulls member counts from all groups
    associated with all courses associated with the root account ID in environment configuration."""

    @transaction.atomic
    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.info("Starting pulling course member counts from Canvas")

        api_client = CanvasApiClient()

        canvas_account_id: int = CANVAS_ACCOUNT_ID
        courses = api_client.get_courses(canvas_account_id=canvas_account_id)
        courses = self.insert_courses(courses)

        all_group_categories = []

        for course in courses:
            group_categories_for_course = api_client.get_group_categories_by_course(course['id'])
            for group_category in group_categories_for_course:
                group_category['course_id'] = course['db_id']

            all_group_categories += group_categories_for_course

        all_group_categories = self.insert_group_categories(all_group_categories)

        all_groups = []

        for group_category in all_group_categories:
            groups_for_course = api_client.get_groups_by_group_category_id(group_category['id'])
            for group in groups_for_course:
                group['group_category_id'] = group_category['db_id']

            all_groups += groups_for_course

        all_db_groups = self.insert_groups(tuple(all_groups))

        logger.info("Finished pulling course member counts from Canvas")


    def insert_courses(self, courses: Tuple[Dict]) -> Tuple[Dict]:
        for course in courses:
            db_course = CourseObservation.objects.create(
                canvas_id=course['id'],
                name=course['name'].strip()
            )
            course['db_id'] = db_course.pk
        return tuple(courses)


    def insert_group_categories(self, group_categories: List[Dict]) -> Tuple[Dict]:
        for group_category in group_categories:
            db_group_category = GroupCategory.objects.create(
                canvas_id=group_category['id'],
                name=group_category['name'].strip(),
                course_id=group_category['course_id']
            )
            group_category['db_id'] = db_group_category.pk
        return tuple(group_categories)


    def insert_groups(self, groups: Tuple[Dict]) -> Tuple[Group]:
        db_groups: List[Group] = []

        for group in groups:
            if group.get("description"):
                group_is_school, org_nr = Utils.get_is_school_and_org_nr(group['description'])
            else:
                group_is_school = False
            if not group_is_school:
                org_nr = None
            is_aggregated = False
            if group['members_count'] < 5:
                is_aggregated = True

            db_group = Group.objects.create(
                canvas_id=group['id'],
                group_category_id=group['group_category_id'],
                name=group['name'].strip(),
                description=group['description'],
                members_count=group['members_count'],
                organization_number=org_nr,
                created_at=group['created_at'],
                aggregated=is_aggregated
            )
            db_groups.append(db_group)
        return tuple(db_groups)
