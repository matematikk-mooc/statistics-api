from datetime import date, datetime, timedelta
from distutils import util
from time import time
from typing import Dict, Set

from django.core.exceptions import ValidationError

from statistics_api.definitions import CATEGORY_CODES

START_DATE_KEY = "from"
END_DATE_KEY = "to"
SHOW_SCHOOLS_KEY = "show_schools"
NR_OF_DATES_LIMIT_KEY = "nr_of_dates_limit"
ENROLLMENT_PERCENTAGE_CATEGORIES_KEY = "enrollment_percentage_categories"
AGGREGATED = "aggregated"


def get_url_parameters_dict(request) -> Dict:
    try:
        STRFTIME_FORMAT = "%Y-%m-%d"
        aggregated: bool = request.GET.get(AGGREGATED)
        start_date_str: str = request.GET.get(START_DATE_KEY)
        end_date_str: str = request.GET.get(END_DATE_KEY)
        if request.GET.get(ENROLLMENT_PERCENTAGE_CATEGORIES_KEY):
            enrollment_percentage_categories: Set[int] = set(
                [int(i.strip()) for i in request.GET.get(ENROLLMENT_PERCENTAGE_CATEGORIES_KEY).split(",")])
        else:
            enrollment_percentage_categories: Set[int] = set(CATEGORY_CODES)

        if not start_date_str and not end_date_str:
            nr_of_dates_limit = 1
        else:
            nr_of_dates_limit = 10000

        start_date: date = (
            datetime.strptime(start_date_str, STRFTIME_FORMAT) if start_date_str else datetime.fromtimestamp(0)).date()

        end_date: date = (datetime.strptime(end_date_str, STRFTIME_FORMAT) if end_date_str else datetime.fromtimestamp(
            int(time()))).date()
        end_date += timedelta(days=1)

        show_schools: bool = bool(util.strtobool(request.GET.get(SHOW_SCHOOLS_KEY, "False")))

        return {START_DATE_KEY: start_date,
                END_DATE_KEY: end_date,
                SHOW_SCHOOLS_KEY: show_schools,
                NR_OF_DATES_LIMIT_KEY: nr_of_dates_limit,
                ENROLLMENT_PERCENTAGE_CATEGORIES_KEY: enrollment_percentage_categories,
                AGGREGATED: aggregated}
    except ValueError:
        raise ValidationError("Invalid parameter value.")
