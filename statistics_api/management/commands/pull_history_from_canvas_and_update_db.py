from datetime import date, timedelta, datetime

from django.core.management import BaseCommand
from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.history.models import History


class Command(BaseCommand):
    help = """Retrieves per-course enrollment activity for all courses administrated by the Canvas account ID
            set in environment settings."""

    def handle(self, *args, **options):
        api_client = CanvasApiClient()
        yesterday = date.today() - timedelta(1)
        accounts = api_client.get_canvas_accounts()
        for account in accounts:
            users = api_client.get_account_users(account.get("id"))
            for user in users:
                self.fetch_user_history(api_client, user.get("id"), yesterday)

    def fetch_user_history(self, api_client, canvas_userid, date):
        history_response = api_client.get_user_history(canvas_userid)
        history = list(
            filter(
                lambda x:
                datetime.strptime(x['visited_at'], '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z') >= datetime.combine(date,
                                                                                                            datetime.min.time()),
                history_response
            )
        )
        for event in history:
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
