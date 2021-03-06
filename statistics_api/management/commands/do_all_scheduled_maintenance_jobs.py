import logging
import sys
from json.decoder import JSONDecodeError

import django
from django.core import management
from django.core.management import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = """This command does performs all scheduled maintenance jobs in correct order."""

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        commands = ("trigger_scheduling_of_kpas_job", "pull_course_member_counts_from_canvas",
                    "fetch_course_enrollment_and_post_to_kpas")

        for command in commands:
            try:
                django.db.close_old_connections()
                management.call_command(command)
            except (JSONDecodeError, AssertionError) as e:
                logger.critical(e)
