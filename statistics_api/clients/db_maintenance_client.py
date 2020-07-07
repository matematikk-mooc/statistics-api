from typing import Tuple

from django.db import connection, transaction

from statistics_api.utils.query_maker import get_update_group_organization_numbers_query


class DatabaseMaintenanceClient:

    @staticmethod
    def update_group_org_nrs(group_ids_and_org_nrs_for_update: Tuple[Tuple[int, str]]) -> None:
        # NB! MAX_ALLOWED_PACKET on MySQL server needs to be higher than default for this line to work.
        # Django ORM is not used here because bulk updates are far too slow, even with bulk_update method
        update_group_organization_numbers_query: str = get_update_group_organization_numbers_query(
            group_ids_and_org_nrs_for_update)

        with connection.cursor() as cursor:
            cursor.execute(update_group_organization_numbers_query)
