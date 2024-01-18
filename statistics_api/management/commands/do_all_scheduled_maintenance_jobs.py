import logging
import sys
from json.decoder import JSONDecodeError

import django
from django.core import management
from django.core.management import BaseCommand

class Command(BaseCommand):
    help = """This command does performs all scheduled maintenance jobs in correct order."""

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        commands = (
            "pull_total_students_counts_from_courses",
            "trigger_scheduling_of_kpas_job",
            "pull_course_member_counts_from_canvas",
            "fetch_course_enrollment_and_post_to_kpas",
            "pull_data_from_matomo",
            "pull_finnish_marks_canvas")

        for command in commands:
            try:
                logger.info(f"Starting command {command}")
                django.db.close_old_connections()
                management.call_command(command)
                logger.info(f"Command {command} finished")
            except (JSONDecodeError, AssertionError) as e:
                logger.critical(e)
