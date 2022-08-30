import logging
import sys

from datetime import date, timedelta

from django.core.management import BaseCommand
from django.db import transaction
import re 
from statistics_api.clients.matomo_api_client import MatomoApiClient
from statistics_api.matomo.models import Visits, PageStatistics


class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        matomo_api_client = MatomoApiClient()
        yesterday = date.today() - timedelta(1)
        self.fetch_visits_and_visitors(matomo_api_client, yesterday)
        self.fetch_page_statistics(matomo_api_client, yesterday)

    @transaction.atomic
    def fetch_visits_and_visitors(self, matomo_api_client, date):
        '''fetch daily visits and visitors whole domain count'''
        visits = matomo_api_client.get_matomo_visits()
        unique_visitors = matomo_api_client.get_matomo_unique_visitors()
        frequency = matomo_api_client.get_matomo_visit_frequency()
        Visits.objects.update_or_create(date=date, defaults={
            'visits' : visits.get('value'),
            'unique_visitors' : unique_visitors.get('value'),
            'unique_visitors_new' : frequency.get('nb_uniq_visitors_new'),
            'unique_visitors_returning' : frequency.get('nb_uniq_visitors_returning'),
            'visits_new' : frequency.get('nb_visits_new'),
            'visits_returning' : frequency.get('nb_visits_returning'),
            'bounce_count_new' : frequency.get('bounce_count_new'),
            'bounce_count_returning' : frequency.get('bounce_count_returning'),
            'sum_visit_length_new' : frequency.get('sum_visit_length_new'),
            'sum_visit_length_returning' : frequency.get('sum_visit_length_returning'),
            'actions_new' : frequency.get('nb_actions_new'),
            'actions_returning' : frequency.get('nb_actions_returning'),
            'max_actions_new' : frequency.get('max_actions_new'),
            'max_actions_returning' : frequency.get('max_actions_returning'),
            'bounce_rate_new' : frequency.get('bounce_rate_new'),
            'bounce_rate_returning' : frequency.get('bounce_rate_returning'),
            'avg_time_on_site_new' : frequency.get('avg_time_on_site_new'),
            'avg_time_on_site_returning' : frequency.get('avg_time_on_site_returning'),
            'actions_per_visit_new' : frequency.get('nb_actions_per_visit_new'),
            'actions_per_visit_returning' : frequency.get('nb_actions_per_visit_returning'),
            })

    @transaction.atomic
    def fetch_page_statistics(self, matomo_api_client, date):
        '''fetch daily statistics for each url in domain'''
        pages = matomo_api_client.get_matomo_page_statistics()
        self.update_db_page_statistics(date, pages)

    def update_db_page_statistics(self, date, pages):
        '''update db with page statistics'''
        for page in pages:
            segment = page.get('segment')
            canvas_course_id = None
            #Get course id from page url
            if segment is not None:
                match = re.search(r'%252Fcourses%252F(\d+)', segment)
                if match:
                    canvas_course_id = match.group(1)
            PageStatistics.objects.create(
                date = date,
                label = page.get('label'),
                url = page.get('url'),
                segment = page.get('segment'),
                visits = page.get('nb_visits'),
                sum_time_spent = page.get('sum_time_spent'), 
                average_time_spent = page.get('avg_time_on_page'),
                unique_visitors = page.get('nb_uniq_visitors'),
                bounce_rate = page.get('bounce_rate'),
                exit_rate = page.get('exit_rate'),
                exit_visits = page.get('exit_nb_visits'),
                entry_visits = page.get('entry_nb_visits'),
                canvas_course_id = canvas_course_id
            )
            if page.get('subtable'):
                self.update_db_page_statistics(date, page['subtable'])
