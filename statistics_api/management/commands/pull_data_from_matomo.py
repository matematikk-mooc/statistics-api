import imp
import logging
import sys

from datetime import date, timedelta

from django.core.management import BaseCommand
from django.db import transaction
 
from statistics_api.clients.matomo_api_client import MatomoApiClient
from statistics_api.matomo.models import Visits


class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        matomoApiClient = MatomoApiClient()
        self.fetch_visits_and_visitors(matomoApiClient)

    
    @transaction.atomic
    def fetch_visits_and_visitors(self, matomoApiClient):
        visits = matomoApiClient.get_matomo_visits()
        unique_visitors = matomoApiClient.get_matomo_unique_visitors()
        yesterday = date.today() - timedelta(1)
        Visits.objects.update_or_create(date=yesterday, defaults={ 'visits' : visits.get('value'), 'unique_visitors' : unique_visitors.get('value')})
