import json
import time
from datetime import date, datetime

from django.test import TestCase
from rest_framework.test import APIClient

from statistics_api.definitions import STRFTIME_FORMAT
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

    def test_county_statistics_for_individual_schools_at_future_date(self):
        """
            Trying to fetch data from the future. Should return 404.
        """
        client = APIClient()
        from_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&from={from_date}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertEqual(0, len(json_response["Result"]))

    def test_county_statistics_by_municipalities(self):
        client = APIClient()
        web_response = client.get(
            path=f"/api/statistics/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("municipalities" in json_response["Result"][0].keys())
