from datetime import date, datetime, timedelta
from distutils import util
from time import time
from typing import Dict, Set

from django.core.exceptions import ValidationError

START_DATE_KEY = "from"
END_DATE_KEY = "to"
SHOW_SCHOOLS_KEY = "show_schools"
NR_OF_DATES_LIMIT_KEY = "nr_of_dates_limit"
AGGREGATED = "aggregated"

def get_url_parameters_dict(request) -> Dict:
    try:
        STRFTIME_FORMAT = "%Y-%m-%d"
        aggregated: str = request.GET.get(AGGREGATED)
        start_date_str: str = request.GET.get(START_DATE_KEY)
        end_date_str: str = request.GET.get(END_DATE_KEY)

        if not start_date_str and not end_date_str:
            nr_of_dates_limit = 1
        else:
            nr_of_dates_limit = 10000

        if aggregated == "1" or aggregated == "True" or aggregated == "true" or aggregated == "TRUE":
            aggregated = True
        elif aggregated == "0" or aggregated == "False" or aggregated == "false" or aggregated == "FALSE":
            aggregated = False

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
                AGGREGATED: aggregated}
    except ValueError:
        raise ValidationError("Invalid parameter value.")
