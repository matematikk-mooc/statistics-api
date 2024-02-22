from datetime import date, timedelta, datetime

from django.core.management import BaseCommand
from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.history.models import History
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()
class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info("Starting fetching recent activity history from Canvas")
        api_client = CanvasApiClient()
        yesterday = date.today() - timedelta(1)
        try:
            accounts = api_client.get_canvas_accounts()
            for account in accounts:
                users = api_client.get_account_users(account.get("id"))
                for user in users:
                    self.fetch_user_history(api_client, user.get("id"), yesterday)
            logger.info("Finished fetching recent activity history from Canvas")
        except Exception as e:
            logger.error("Error while fetching recent activity history from Canvas: " + str(e))

    def fetch_user_history(self, api_client, canvas_userid, date):
        try:
            history_response = api_client.get_user_history(canvas_userid)
            history = [
                event for event in history_response
                if datetime.strptime(event['visited_at'], '%Y-%m-%dT%H:%M:%SZ') >= datetime.combine(date, datetime.min.time())
            ]
            for event in history:
                try:
                    History.objects.get_or_create(
                        canvas_userid=canvas_userid,
                        visited_at=event.get('visited_at'),
                        defaults={
                            'asset_code': event.get('asset_code'),
                            'context_id': event.get('context_id'),
                            'context_type': event.get('context_type'),
                            'visited_url': event.get('visited_url'),
                            'interaction_seconds': event.get('interaction_seconds'),
                            'asset_icon': event.get('asset_icon'),
                            'asset_readable_category': event.get('asset_readable_category'),
                            'asset_name': event.get('asset_name'),
                            'context_name': event.get('context_name')
                        }
                    )
                except Exception as e:
                    logger.error("Error while saving history: " + event.get('context_name') + ", " + str(e))
                    logger.info("Asset code: " + event.get('asset_code'))
        except Exception as e:
            logger.error("Error while fetching history for user " + canvas_userid + ": " + str(e))
