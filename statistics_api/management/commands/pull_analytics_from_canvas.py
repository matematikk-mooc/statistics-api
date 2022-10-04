import logging
import sys
from datetime import date, timedelta
from django.core.management import BaseCommand
from django.db import transaction

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from statistics_api.analytics.models import CanvasAnalytics

class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id=canvas_account_id)
        yesterday = date.today() - timedelta(1)
        for course in courses:
            course_id = course.get("id")
            self.pull_analytics(api_client, course_id, yesterday)

    def pull_analytics(self, api_client, course_id, yesterday):
        analytics = api_client.get_course_analytics(course_id)
        if analytics is None:
            print("Analytics/activity endpoint does not exists for course ", course_id)
            return
        yesterday_analytics = list(
                filter(
                    lambda x:
                        x["date"] == yesterday,
                        analytics
                )
            )
        if yesterday_analytics == []:
            print("No analytics/activity data registrered for course, ", course_id, " yesterday, ", yesterday)
            return
        yesterday_analytics = yesterday_analytics[0]
        CanvasAnalytics.objects.create(
            course_id = course_id,
            date = yesterday_analytics.get("date"),
            views = yesterday_analytics.get("views"),
            participations = yesterday_analytics.get("participations")
        )
