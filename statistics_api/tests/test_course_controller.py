import json
import time
import warnings
from datetime import datetime, timedelta

from django.test import TestCase
from rest_framework.test import APIClient
from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_ACCOUNT_ID


class Test(TestCase):

    def test_course(self):

        canvas_api_client = CanvasApiClient()
        courses = canvas_api_client.get_courses(CANVAS_ACCOUNT_ID)
        from_date = str(datetime.fromtimestamp(int(time.time())).date() - timedelta(days=30))

        for course in courses:
            client = APIClient()
            web_response = client.get(
                path=f"/api/statistics/{course['id']}?from={from_date}")
            self.assertEqual(200, web_response.status_code)
            json_response = json.loads(web_response.content)
            self.assertNotEqual(json_response["Result"][0]['enrollment_count'], None)