import logging
import sys

from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from statistics_api.canvas_users.models import CanvasUser

class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id=canvas_account_id)
        for course in courses:
            course_id = course.get('id')
            if course_id == 360:
                continue
            groups = api_client.get_course_groups(course_id)
            filtered_groups = list(
                filter(
                    lambda x:
                        x["members_count"] > 0,
                        groups
                )
            )
            for group in filtered_groups:
                group_id = group.get('id')
                group_name = group.get('name')
                group_description = group.get('description')
                member_count = group.get("members_count")
                self.fetch_group_users(api_client, course_id, group_id, group_name, group_description, member_count)


    @transaction.atomic
    def fetch_group_users(self, api_client, course_id, group_id, group_name, group_description, member_count):
        if  member_count is not None and member_count > 0:  
            users = api_client.get_group_users(group_id)
            if users is None:
                return
            for user in users:
                canvas_user_id = user.get('id')
                CanvasUser.objects.get_or_create(
                    canvas_user_id = canvas_user_id,
                    course_id = course_id,
                    group_id = group_id,
                    defaults={
                        "group_name" : group_name,
                        "group_description" : group_description
                        })
        else: 
            print("Count is 0. Group: ", group_name)