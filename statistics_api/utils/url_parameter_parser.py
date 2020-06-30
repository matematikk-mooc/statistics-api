from datetime import date, datetime
from distutils import util
from time import time
from typing import Tuple

from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest


def get_url_parameters(request: WSGIRequest) -> Tuple[date, date, bool]:
    try:
        STRFTIME_FORMAT = "%Y-%m-%d"

        start_date_str: str = request.GET.get('from')
        end_date_str: str = request.GET.get('to')

        start_date: date = (
            datetime.strptime(start_date_str, STRFTIME_FORMAT) if start_date_str else datetime.fromtimestamp(0)).date()

        end_date: date = (datetime.strptime(end_date_str, STRFTIME_FORMAT) if end_date_str else datetime.fromtimestamp(
            int(time()))).date()

        show_schools: bool = bool(util.strtobool(request.GET.get('show_schools', "False")))

        return start_date, end_date, show_schools
    except ValueError:
        raise ValidationError("Invalid parameter value.")
