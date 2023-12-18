import logging
import sys

from django.core.management import BaseCommand
from statistics_api.definitions import CANVAS_ACCOUNT_ID
from statistics_api.total_students.models import TotalStudents
from statistics_api.clients.canvas_api_client import CanvasApiClient

class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.info("Starting pulling total student counts from Canvas")
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id)
        for course in courses:
            TotalStudents.objects.create(
                course_id=course.get('id'),
                total_students=course.get('total_students')
            )
        logger.info("Finished pulling total student counts from Canvas")
