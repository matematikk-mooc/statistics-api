import json
import time
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from statistics_api.models.course_observation import CourseObservation
from statistics_api.services.course_service import compute_total_nr_of_students_for_course_observation


class Test(TestCase):

    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()

        cls.COUNTY_ID = 15
        distinct_course_observation_canvas_ids = [i[CourseObservation.canvas_id.field.name] for i in
                                                  CourseObservation.objects.values(
                                                      CourseObservation.canvas_id.field.name).distinct()]

        most_recent_observations_for_courses = []

        for course_canvas_id in distinct_course_observation_canvas_ids:
            most_recent_course_observation = CourseObservation.objects.filter(canvas_id=course_canvas_id).order_by(
                f"-{CourseObservation.date_retrieved.field.name}")[0]
            most_recent_observations_for_courses.append(most_recent_course_observation)

        c: CourseObservation
        most_recent_observation_of_course_with_most_members = max(most_recent_observations_for_courses,
                                                                  key=lambda
                                                                      c: compute_total_nr_of_students_for_course_observation(
                                                                      c))

        cls.CANVAS_COURSE_ID = most_recent_observation_of_course_with_most_members.canvas_id

    def test_county_statistics_for_individual_schools(self):
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&to={current_date}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())
        self.assertNotEqual(json_response["info"]['category_codes'], None)

    def test_county_statistics_for_individual_schools_in_enrollment_percentage_category_1(self):
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&to={current_date}&enrollment_percentage_categories=1")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())
        self.assertNotEqual(json_response["info"]['category_codes'], None)
        for school in json_response["Result"][0]["schools"]:
            self.assertEqual(school["enrollment_percentage_category"], 1)

    def test_county_statistics_for_individual_schools_in_enrollment_percentage_categories_0_and_5(self):
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&to={current_date}&enrollment_percentage_categories=0,5")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())
        self.assertNotEqual(json_response["info"]['category_codes'], None)
        for school in json_response["Result"][0]["schools"]:
            self.assertTrue(school["enrollment_percentage_category"] in (0, 5))

    def test_county_statistics_for_individual_schools_without_date_intervals(self):
        """
            Trying to fetch county school data without specifying a date interval. Should only return the most recent
            observation.
        """
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())
        self.assertEqual(1, len(json_response["Result"]))
        self.assertNotEqual(json_response["info"]['category_codes'], None)

    def test_county_statistics_for_individual_schools_at_future_date(self):
        """
            Trying to fetch data from the future. Should return empty result set.
        """
        client = APIClient()
        from_date = str(datetime.fromtimestamp(int(time.time())).date() + timedelta(days=1))
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&from={from_date}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertEqual(0, len(json_response["Result"]))
        self.assertNotEqual(json_response["info"]['category_codes'], None)

    def test_county_statistics_with_invalid_URL_parameter(self):
        """
            Trying to pass illegal values as URL parameters. Should get ValidationError.
        """
        client = APIClient()
        try:
            client.get(
                path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=foo&from=bar")
            self.fail()
        except ValidationError:
            pass

    def test_county_statistics_by_municipalities(self):
        client = APIClient()
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("municipalities" in json_response["Result"][0].keys())

        municipality_names_list = [municipality["name"] for municipality in json_response["Result"][0]["municipalities"]]
        self.assertEqual(len(municipality_names_list), len(set(municipality_names_list)))
        self.assertNotEqual(json_response["info"]['category_codes'], None)

    def test_county_statistics_by_municipalities_should_not_return_newer_entries_than_end_date(self):
        client = APIClient()
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?from=1970-01-01")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("municipalities" in json_response["Result"][0].keys())

        # "%Y-%m-%dT%H:%M:%S.%fZ"
        oldest_date_in_result = datetime.strptime(json_response["Result"][-1]["date"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        oldest_date_in_result_str = oldest_date_in_result + timedelta(days=1)

        second_web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?to={oldest_date_in_result_str}")
        self.assertEqual(200, web_response.status_code)

        second_json_response = json.loads(second_web_response.content)

        for date_str in [res["date"] for res in second_json_response["Result"]]:
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            self.assertTrue(oldest_date_in_result >= date)
