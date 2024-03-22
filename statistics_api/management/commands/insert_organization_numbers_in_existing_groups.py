import logging
import sys
from typing import List, Tuple

from django.core.management import BaseCommand
from django.db import connection

from statistics_api.course_info.utils import get_is_school_and_org_nr
from statistics_api.definitions import DB_DATABASE
from statistics_api.course_info.models import Group


class Command(BaseCommand):
    help = """This command retroactively inserts organization numbers to existing `Group` rows in the database."""

    def handle(self, *args, **options):

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.info("Starting inserting organization numbers to existing `Group` rows in the database...")
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
        self.update_group_org_nrs(tuple(group_ids_and_org_nrs_for_update))
        logger.info(f"Finished inserting organization numbers to existing `Group` rows in the database.")


    def update_group_org_nrs(self, group_ids_and_org_nrs_for_update: Tuple[Tuple[int, str]]) -> None:
        # NB! MAX_ALLOWED_PACKET on MySQL server needs to be higher than default for this line to work.
        # Django ORM is not used here because bulk updates are far too slow, even with bulk_update method
        update_group_organization_numbers_query = self.get_update_group_organization_numbers_query(
            group_ids_and_org_nrs_for_update)

        with connection.cursor() as cursor:
            cursor.execute(update_group_organization_numbers_query)
            cursor.close()


    def get_update_group_organization_numbers_query(self, group_ids_and_org_nrs: Tuple[Tuple[int, str]]) -> str:
        sql_values = []

        for group_id, group_org_nr in group_ids_and_org_nrs:
            sql_values.append(
                f"({group_id}, {0}, '', NULL, {0}, {0}, {0}, {1}, '{group_org_nr}')")

        return f"""INSERT INTO `group` VALUES\n""" \
            + ", \n".join(sql_values) + \
            f"""\nON DUPLICATE KEY UPDATE organization_number = VALUES(organization_number)"""