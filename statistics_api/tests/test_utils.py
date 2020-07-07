import json
from unittest.case import TestCase

from statistics_api.definitions import ROOT_DIR
from statistics_api.utils.utils import calculate_enrollment_percentage_category, filter_high_schools


class TestFilterHighSchools(TestCase):

    def test_filter_high_schools(self):
        with open(f"{ROOT_DIR}/tests/data/api_nsr_counties_15_school.txt") as f:
            web_response_dict = json.loads(f.read())

        schools = web_response_dict["result"]
        self.assertEqual(282, len(schools))
        high_schools = filter_high_schools(schools)
        self.assertEqual(32, len(high_schools))



class TestCalculateEnrollmentPercentageCategory(TestCase):

    def test_calculate_enrollment_percentage_category_twenty_percent_should_return_category_1(self):
        enrollment_count = 20
        teacher_count = 100

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(1, enrollment_percentage_category)

    def test_calculate_enrollment_percentage_category_fifty_percent_should_return_category_2(self):
        enrollment_count = 50
        teacher_count = 100

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(3, enrollment_percentage_category)

    def test_calculate_enrollment_percentage_category_hundredandten_percent_should_return_category_5(self):
        enrollment_count = 110
        teacher_count = 100

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(5, enrollment_percentage_category)

    def test_calculate_enrollment_percentage_category_over_twenty_percent_should_return_category_2(self):
        enrollment_count = 2001
        teacher_count = 10000

        enrollment_percentage_category = calculate_enrollment_percentage_category(enrollment_count, teacher_count)

        self.assertEqual(2, enrollment_percentage_category)