import logging
import sys

from threading import Thread
from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from statistics_api.canvas_users.models import CanvasUser


class Command(BaseCommand):

    @transaction.atomic
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
            midle_index = len(filtered_groups) // 2
            first_half = filtered_groups[:midle_index]
            second_half = filtered_groups[midle_index:]
            threads = [Thread(target=self.parse_groups, args=(api_client, first_half, course_id)),
                       Thread(target=self.parse_groups, args=(api_client, second_half, course_id))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

    def parse_groups(self, api_client, groups, course_id):
        for group in groups:
            group_id = group.get('id')
            group_name = group.get('name')
            group_description = group.get('description')
            self.fetch_group_users(api_client, course_id, group_id, group_name, group_description)

    @transaction.atomic
    def fetch_group_users(self, api_client, course_id, group_id, group_name, group_description):
        users = api_client.get_group_users(group_id)
        if users is None:
            return
        objects_to_add = []
        self.parse_users(users, objects_to_add, course_id, group_id, group_name, group_description)
        CanvasUser.objects.bulk_create(objects_to_add)

    def parse_users(self, queue_users, objects_to_add, course_id, group_id, group_name, group_description):
        for user in queue_users:
            canvas_user_id = user.get('id')
            exists = CanvasUser.objects.filter(canvas_user_id=canvas_user_id, course_id=course_id,
                                               group_id=group_id).exists()
            if not exists:
                new_user = CanvasUser(
                    canvas_user_id=canvas_user_id,
                    course_id=course_id,
                    group_id=group_id,
                    group_name=group_name,
                    group_description=group_description
                )
                objects_to_add.append(new_user)
