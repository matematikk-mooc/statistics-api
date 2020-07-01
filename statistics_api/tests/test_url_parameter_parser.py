from datetime import date
from unittest import TestCase

from rest_framework.test import APIRequestFactory

from statistics_api.utils.url_parameter_parser import get_url_parameters


class Test(TestCase):

    def test_get_url_parameters(self):
        factory = APIRequestFactory()
        request = factory.get(path="/foo?from=2020-01-02&to=2020-01-05&show_schools=True")
        start_date, end_date, show_schools, nr_of_dates_limit = get_url_parameters(request)
        self.assertTupleEqual((date(year=2020, month=1, day=2), date(year=2020, month=1, day=5), True, 10000),
                              (start_date, end_date, show_schools, 10000))

    def test_get_url_parameters_without_date_intervals(self):
        factory = APIRequestFactory()
        request = factory.get(path="/foo?show_schools=True")
        start_date, end_date, show_schools, nr_of_dates_limit = get_url_parameters(request)
        self.assertTupleEqual((date(year=1970, month=1, day=1), True, nr_of_dates_limit),
                              (start_date, show_schools, 1))