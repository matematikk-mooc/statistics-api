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
            "pull_course_member_counts_from_canvas",
            "fetch_course_enrollment_activity",
            "pull_data_from_matomo",
            "pull_finnish_marks_canvas",
            "pull_history_from_canvas_and_update_db",
            "pull_course_group_registrations",
            )

        for command in commands:
            try:
                logger.info(f"Starting command {command}")
                django.db.close_old_connections()
                management.call_command(command)
                logger.info(f"Command {command} finished")
            except (JSONDecodeError, AssertionError) as e:
                logger.error(e)
