import logging

from django.core.management import BaseCommand
from statistics_api.clients.canvas_api_client import CanvasApiClient



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("account_id", nargs="+", type=int)

    def handle(self, *args, **options):
        account_id=options["account_id"][0]
        api_client = CanvasApiClient()
        account_dev_users = api_client.get_udirdev_account_users(account_id)
        for user in account_dev_users:
            if self.check_email(user.get("email")):
                api_client.delete_user(account_id, user.get("id"))
                print("Deleted user: ", user.get("id"), ", ", user.get("email"))

    def check_email(self, email):
        return email.lower().endswith("@udir.dev")
