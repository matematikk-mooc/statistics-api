from django.core.management import BaseCommand

from statistics_api.clients.kpas_client import KpasClient
import logging
import sys

class Command(BaseCommand):
    help = """This command does NOT trigger a scheduled job at the KPAS LTI module, but it ensures that an already scheduled
        job remains on schedule."""

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        kpas_client = KpasClient()
        logger.info("Starting trigger scheduling of KPAS job")
        kpas_client.post_trigger_to_activate_schedule_of_job()
        logger.info("Finished trigger scheduling of KPAS job")
