import logging
import sys
from typing import List, Tuple

from django.core.management import BaseCommand

from statistics_api.clients.db_client import get_is_school_and_org_nr
from statistics_api.clients.db_maintenance_client import DatabaseMaintenanceClient
from statistics_api.definitions import DB_DATABASE
from statistics_api.models.group import Group


class Command(BaseCommand):
    help = """This command retroactively inserts organization numbers to existing `Group` rows in the database."""

    def handle(self, *args, **options):

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()

        all_db_groups = Group.objects.all()

        group_ids_and_org_nrs_for_update: List[Tuple[int, str]] = []

        for db_group in all_db_groups:
            db_group: Group
            if db_group.description:
                group_is_school, org_nr = get_is_school_and_org_nr(db_group.description)
                if group_is_school:
                    db_group.organization_number = org_nr
                    group_ids_and_org_nrs_for_update.append((db_group.pk, db_group.organization_number))

        logger.info(f"Updating organization numbers on {len(group_ids_and_org_nrs_for_update)} groups in {DB_DATABASE}...")
        DatabaseMaintenanceClient.update_group_org_nrs(tuple(group_ids_and_org_nrs_for_update))
