from datetime import date
from unittest import TestCase

from rest_framework.test import APIRequestFactory

from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, NR_OF_DATES_LIMIT_KEY, SHOW_SCHOOLS_KEY, \
    END_DATE_KEY, START_DATE_KEY


class Test(TestCase):

    def test_get_url_parameters(self):
        factory = APIRequestFactory()
        request = factory.get(path="/foo?from=2020-01-02&to=2020-01-05&show_schools=True")
        url_param_dict = get_url_parameters_dict(request)
        self.assertTupleEqual((date(year=2020, month=1, day=2), date(year=2020, month=1, day=6), True, 10000),
                              (url_param_dict[START_DATE_KEY], url_param_dict[END_DATE_KEY], url_param_dict[SHOW_SCHOOLS_KEY], url_param_dict[NR_OF_DATES_LIMIT_KEY]))

    def test_get_url_parameters_without_date_intervals(self):
        factory = APIRequestFactory()
        request = factory.get(path="/foo?show_schools=True")
        url_param_dict = get_url_parameters_dict(request)
        self.assertTupleEqual((date(year=1970, month=1, day=1), True, 1),
                              (url_param_dict[START_DATE_KEY], url_param_dict[SHOW_SCHOOLS_KEY], url_param_dict[NR_OF_DATES_LIMIT_KEY]))