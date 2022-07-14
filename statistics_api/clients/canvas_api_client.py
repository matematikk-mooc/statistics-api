import json
from typing import Tuple, List, Dict

import requests

from statistics_api.definitions import CANVAS_ACCESS_KEY, CANVAS_API_URL, CA_FILE_PATH


class CanvasApiClient:

    def __init__(self):
        self.web_session = requests.Session()
        self.web_session.headers.update({
            "Authorization": f"Bearer {CANVAS_ACCESS_KEY}"
        })

        try:
            self.web_session.get(CANVAS_API_URL)
        except requests.exceptions.SSLError:
            # If current CA triggers SSL error, try custom CA
            self.web_session.verify = CA_FILE_PATH if CA_FILE_PATH else self.web_session.verify

    def get_group_categories_by_course(self, course_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/group_categories?per_page=100"
        return self.paginate_through_url(url)

    def get_groups_by_group_category_id(self, group_category_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/group_categories/{group_category_id}/groups?per_page=100"
        return self.paginate_through_url(url)

    def get_courses(self, canvas_account_id: int) -> Tuple[Dict]:
        """
            Fetching all courses to which the configured account is root account of.
        :return:
        """
        url = f"{CANVAS_API_URL}/accounts/{canvas_account_id}/courses?include[]=total_students&per_page=100"
        return self.paginate_through_url(url)

    def get_course(self, canvas_course_id: int) -> Dict:
        url = f"{CANVAS_API_URL}/courses/{canvas_course_id}?include[]=total_students"
        return self.get_single_element_from_url(url)

    def get_single_element_from_url(self, target_url) -> Dict:
        web_response = self.web_session.get(target_url)
        if web_response.status_code == 204:
            return None
        if web_response.status_code != 200:
            raise AssertionError(f"Could not retrieve data from Canvas LMS instance at {CANVAS_API_URL}")

        return json.loads(web_response.text)

    def paginate_through_url(self, target_url: str, current_items: List = None) -> Tuple[Dict]:
        if current_items is None:
            current_items = []

        web_response = self.web_session.get(target_url)
        if web_response.status_code != 200:
            print(web_response)
            raise AssertionError(f"Could not retrieve data from Canvas LMS instance at {CANVAS_API_URL}")
        new_items = json.loads(web_response.text)
        current_items += new_items
        if web_response.links.get('next'):
            next_page_url = web_response.links['next'].get('url')
            return self.paginate_through_url(target_url=next_page_url, current_items=current_items)
        else:
            return tuple(current_items)

    def get_canvas_account_id_of_current_user(self) -> int:
        web_response = self.web_session.get(f"{CANVAS_API_URL}/users/self")
        account_json = json.loads(web_response.text)
        return int(account_json['id'])

    def get_user_history(self, canvas_userid: int) -> Dict:
        url = f"{CANVAS_API_URL}/users/{canvas_userid}/history"
        return self.get_single_element_from_url(url)

    def get_quizzes_in_course(self, course_id):
        '''Get all quizzes in a given course'''
        url = f"{CANVAS_API_URL}/courses/{course_id}/quizzes?per_page=100"
        return self.paginate_through_url(url)

    def get_quiz_statistics(self, course_id: int, quiz_id: int) -> Dict:
        '''Get statistics for a given quiz'''
        url = f"{CANVAS_API_URL}/courses/{course_id}/quizzes/{quiz_id}/statistics"
        return self.get_single_element_from_url(url)

    # Below code might be used for open answer questions
    #def get_submissions_in_quiz(self, course_id, quiz_id):
    #    '''Get submissions in a given quiz'''
    #    url = f"{CANVAS_API_URL}/courses/{course_id}/quizzes/{quiz_id}/submissions?per_page=100"
    #    return self.paginate_through_url(url)

    #def get_submission_events(self, course_id, quiz_id, submission_id):
    #    url = f"{CANVAS_API_URL}/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/events?per_page=100"
    #    return self.paginate_through_url(url)

