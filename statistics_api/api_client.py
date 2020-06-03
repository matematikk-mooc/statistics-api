import json
from typing import Tuple

import requests

from statistics_api.definitions import CANVAS_ACCESS_KEY, CANVAS_API_URL, CANVAS_ACCOUNT_ID, CA_FILE_PATH

class ApiClient:

    def __init__(self):
        self.web_session = requests.Session()
        self.web_session.headers.update({
            "Authorization": f"Bearer {CANVAS_ACCESS_KEY}"
        })

        self.web_session.verify = CA_FILE_PATH

    def get_group_categories_by_course(self, course_id: int) -> Tuple:
        web_response = self.web_session.get(f"{CANVAS_API_URL}/courses/{course_id}/group_categories")
        return tuple(json.loads(web_response.text))

    def get_groups_by_group_category_id(self, group_category_id: int):
        web_response = self.web_session.get(f"{CANVAS_API_URL}/group_categories/{group_category_id}/groups",
                                            params={"include[]": "last_activity_at"})
        return tuple(json.loads(web_response.text))

    def get_courses(self):
        """
            Fetching all courses to which the configured account is root account of.
        :return:
        """
        web_response = self.web_session.get(f"{CANVAS_API_URL}/users/{CANVAS_ACCOUNT_ID}/courses",
                                            params={'include[]': 'total_students'})
        courses_dicts = json.loads(web_response.text)
        return courses_dicts
