import json

from rest_framework.test import APIClient

from statistics_api.tests.county_controller_base_test import CountyControllerBaseTest


class Test(CountyControllerBaseTest):

    def test_county_high_school_statistics_by_county_id(self):
        client = APIClient()
        web_response = client.get(
            path=f"/api/statistics/high_schools/county/{self.COUNTY_ID}/course/{self.CANVAS_COURSE_ID}")
        self.assertEqual(200, web_response.status_code)
        json.loads(web_response.content)

    def test_county_high_school_statistics_by_county_id_with_non_existing_id(self):
        client = APIClient()
        web_response = client.get(
            path=f"/api/statistics/high_schools/county/1100/course/{self.CANVAS_COURSE_ID}")
        self.assertEqual(404, web_response.status_code)