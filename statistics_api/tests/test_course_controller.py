import json
import warnings

from django.test import TestCase
from rest_framework.test import APIClient
from statistics_api.clients.canvas_api_client import CanvasApiClient


class Test(TestCase):

    def test_course(self):
        required_nr_of_course_observations = 3

        canvas_api_client = CanvasApiClient()
        canvas_account_id = canvas_api_client.get_canvas_account_id_of_current_user()
        courses = canvas_api_client.get_courses(canvas_account_id)

        for course in courses:
            client = APIClient()
            web_response = client.get(
                path=f"/api/statistics/{course['id']}?nr_of_dates={required_nr_of_course_observations}")
            self.assertEqual(200, web_response.status_code)
            json_response = json.loads(web_response.content)
            self.assertNotEqual(json_response["Result"][0]['antallBrukere'], None)

            if len(json_response["Result"]) < required_nr_of_course_observations:
                warnings.warn(
                    f"Test database needs {required_nr_of_course_observations} course observations to conduct all tests")
                return
            else:
                second_web_response = client.get(
                path=f"/api/statistics/{course['id']}?nr_of_dates={required_nr_of_course_observations-1}&nr_of_dates_offset=1")
                second_json_response = json.loads(second_web_response.content)
                self.assertEqual(second_json_response["Result"][0]['date'], json_response["Result"][1]['date'])