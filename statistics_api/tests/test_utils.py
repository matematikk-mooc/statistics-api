import json
from django.test import TestCase

from statistics_api.definitions import ROOT_DIR
from statistics_api.utils.utils import calculate_enrollment_percentage_category, filter_high_schools, \
    parse_year_from_data_file_name, get_primary_school_data_file_paths, get_county_data_file_paths


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


class TestParseYearFromDataFileName(TestCase):
    def test_parse_year_from_data_file_name(self):
        year_of_data = parse_year_from_data_file_name('primary_schools_data_2019.csv')

        self.assertEqual(2019, year_of_data)


class TestGetPrimarySchoolDataFilePaths(TestCase):
    def test_get_primary_school_data_file_paths(self):
        file_paths = get_primary_school_data_file_paths(f"{ROOT_DIR}tests/data/")
        self.assertEqual(2, len(file_paths))
        file_names = [p.split("/")[-1] for p in file_paths]
        file_names.sort()
        self.assertListEqual(['primary_schools_data_2019.csv', 'primary_schools_data_2020.csv'], file_names)


class TestGetCountyDataFilePaths(TestCase):
    def test_get_county_data_file_paths(self):
        file_paths = get_county_data_file_paths(f"{ROOT_DIR}tests/data/")
        self.assertEqual(1, len(file_paths))
        file_name = file_paths[0].split("/")[-1]
        self.assertEqual('county_data_2018.csv', file_name)
