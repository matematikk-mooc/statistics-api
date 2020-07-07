from django.core.management import BaseCommand

from statistics_api.clients.kpas_client import KpasClient


class Command(BaseCommand):
    help = """This command does NOT trigger a scheduled job at the KPAS LTI module, but it ensures that an already scheduled
        job remains on schedule."""

    def handle(self, *args, **options):
        kpas_client = KpasClient()
        kpas_client.post_trigger_to_activate_schedule_of_job()
