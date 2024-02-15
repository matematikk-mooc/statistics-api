import logging
import sys

from datetime import date, timedelta

from django.core.management import BaseCommand
from django.db import transaction
import re
from statistics_api.clients.matomo_api_client import MatomoApiClient
from statistics_api.matomo.models import Visits, PageStatistics

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()
class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info("Starting pulling data from Matomo")
        matomo_api_client = MatomoApiClient()
        yesterday = date.today() - timedelta(1)
        try:
            self.fetch_visits_and_visitors(matomo_api_client, yesterday)
            self.fetch_page_statistics(matomo_api_client, yesterday)
            logger.info("Finished pulling data from Matomo")
        except Exception as e:
            logger.error("Error pulling data from Matomo: " + str(e))

    @transaction.atomic
    def fetch_visits_and_visitors(self, matomo_api_client, date):
        '''fetch daily visits and visitors whole domain count'''

        visits = matomo_api_client.get_matomo_visits()
        unique_visitors = matomo_api_client.get_matomo_unique_visitors()
        frequency = matomo_api_client.get_matomo_visit_frequency()
        Visits.objects.update_or_create(date=date, defaults={
            'visits': visits.get('value'),
            'unique_visitors': unique_visitors.get('value'),
            'unique_visitors_new': frequency.get('nb_uniq_visitors_new'),
            'unique_visitors_returning': frequency.get('nb_uniq_visitors_returning'),
            'visits_new': frequency.get('nb_visits_new'),
            'visits_returning': frequency.get('nb_visits_returning'),
            'bounce_count_new': frequency.get('bounce_count_new'),
            'bounce_count_returning': frequency.get('bounce_count_returning'),
            'sum_visit_length_new': frequency.get('sum_visit_length_new'),
            'sum_visit_length_returning': frequency.get('sum_visit_length_returning'),
            'actions_new': frequency.get('nb_actions_new'),
            'actions_returning': frequency.get('nb_actions_returning'),
            'max_actions_new': frequency.get('max_actions_new'),
            'max_actions_returning': frequency.get('max_actions_returning'),
            'bounce_rate_new': frequency.get('bounce_rate_new'),
            'bounce_rate_returning': frequency.get('bounce_rate_returning'),
            'avg_time_on_site_new': frequency.get('avg_time_on_site_new'),
            'avg_time_on_site_returning': frequency.get('avg_time_on_site_returning'),
            'actions_per_visit_new': frequency.get('nb_actions_per_visit_new'),
            'actions_per_visit_returning': frequency.get('nb_actions_per_visit_returning'),
        })


    @transaction.atomic
    def fetch_page_statistics(self, matomo_api_client, date):
        '''fetch daily statistics for each url in domain'''
        pages = matomo_api_client.get_matomo_page_statistics()
        self.page_statistics(date, pages, None)


    def page_statistics(self, date, pages, canvas_course_id):
        '''update db with page statistics'''
        for page in pages:
            self.update_db(date, page, canvas_course_id)
            if page.get('subtable') and page.get('label') == 'courses':
                self.main_course_page(date, page['subtable'])
            elif page.get('subtable'):
                self.page_statistics(date, page['subtable'], canvas_course_id)

    def main_course_page(self, date, pages):
        for page in pages:
            label = page.get('label')
            canvas_course_id = ""
            for i, character in enumerate(label):
                if character.isdigit():
                    canvas_course_id += character
                if not character.isdigit() and len(canvas_course_id) > 0:
                    break
            self.update_db(date, page, canvas_course_id)
            if page.get('subtable'):
                self.page_statistics(date, page['subtable'], canvas_course_id)

    def update_db(self, date, page, canvas_course_id):
        # Ignore login pages, this should be done in a better way
        # when we have more information about how matomo statistics will be used
        if(page.get('url') != None
           and 'login/saml' in page.get('url')
           or 'login_hint' in page.get('label')
           or page.get('segment') != None and 'login_hint' in page.get('segment')):
            return
        try:
            PageStatistics.objects.create(
                date=date,
                label=page.get('label'),
                url=page.get('url'),
                segment=page.get('segment'),
                visits=page.get('nb_visits'),
                sum_time_spent=page.get('sum_time_spent'),
                average_time_spent=page.get('avg_time_on_page'),
                unique_visitors=page.get('nb_uniq_visitors'),
                bounce_rate=page.get('bounce_rate'),
                exit_rate=page.get('exit_rate'),
                exit_visits=page.get('exit_nb_visits'),
                entry_visits=page.get('entry_nb_visits'),
                canvas_course_id=canvas_course_id
            )
        except Exception as e:
            logger.error("Error updating page: " + page.get('url') + ", statistics from Matomo: " + str(e))
            raise e