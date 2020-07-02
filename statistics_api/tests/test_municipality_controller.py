import json
import time
from datetime import datetime

from django.test import TestCase
from rest_framework.test import APIClient

from statistics_api.models.course_observation import CourseObservation
from statistics_api.services.course_service import compute_total_nr_of_students_for_course_observation


class Test(TestCase):

    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()

        cls.MUNICIPALITY_ID = "0301"
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

    def test_municipality_statistics(self):
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/municipality/{self.MUNICIPALITY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&to={current_date}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())

    def test_municipality_statistics_for_individual_schools_in_enrollment_percentage_category_2(self):
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/municipality/{self.MUNICIPALITY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&to={current_date}&enrollment_percentage_categories=2")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())
        for school in json_response["Result"][0]["schools"]:
            self.assertEqual(school["enrollment_percentage_category"], 2)

    def test_municipality_statistics_for_individual_schools_in_enrollment_percentage_categories_1_and_4(self):
        client = APIClient()
        current_date = str(datetime.fromtimestamp(int(time.time())).date())
        web_response = client.get(
            path=f"/api/statistics/municipality/{self.MUNICIPALITY_ID}/course/{self.CANVAS_COURSE_ID}?show_schools=True&to={current_date}&enrollment_percentage_categories=1,4")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())
        for school in json_response["Result"][0]["schools"]:
            self.assertTrue(school["enrollment_percentage_category"] in (1, 4))

    def test_municipality_statistics_for_individual_schools_in_empty_municipality(self):
        client = APIClient()
        web_response = client.get(
            path=f"/api/statistics/municipality/{3450}/course/{self.CANVAS_COURSE_ID}")
        self.assertEqual(200, web_response.status_code)

        json_response = json.loads(web_response.content)
        self.assertTrue("schools" in json_response["Result"][0].keys())