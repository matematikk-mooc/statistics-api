import json

from django.test import TestCase
from rest_framework.test import APIClient


class Test(TestCase):

    def test_course(self):

        course_ids = (360, 289)
        from_date = '2020-06-30'

        for course_id in course_ids:
            client = APIClient()
            web_response = client.get(
                path=f"/api/statistics/{course_id}?from={from_date}")
            self.assertEqual(200, web_response.status_code)
            json_response = json.loads(web_response.content)
            self.assertNotEqual(json_response["Result"][0]['enrollment_count'], None)
