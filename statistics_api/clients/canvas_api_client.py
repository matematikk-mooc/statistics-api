import datetime
import json
from typing import Tuple, List, Dict
from urllib import response

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
        if web_response.status_code in (204, 404):
            return None
        if web_response.status_code != 200:
            print(web_response.status_code)
            raise AssertionError(f"Could not retrieve data from Canvas LMS instance at {CANVAS_API_URL}")

        return json.loads(web_response.text)

    def paginate_through_url(self, target_url: str, current_items: List = None) -> Tuple[Dict]:
        if current_items is None:
            current_items = []
        web_response = self.web_session.get(target_url)
        if web_response.status_code != 200:
            print(web_response)
            raise AssertionError(f"Could not retrieve data from Canvas LMS instance at {target_url}")
        new_items = json.loads(web_response.text)
        current_items += new_items
        if web_response.links.get('next'):
            next_page_url = web_response.links['next'].get('url')
            return self.paginate_through_url(target_url=next_page_url, current_items=current_items)
        return tuple(current_items)

    def paginate_through_url_module_items(self, target_url: str, current_items: List = None) -> Tuple[Dict]:
        if current_items is None:
            current_items = []
        web_response = self.web_session.get(target_url)
        if web_response.status_code in (401, 403):
            print("Response code not 200 ", web_response.status_code)
            print(target_url)
            print(web_response.text)
            return None
        if web_response.status_code != 200:
            print(web_response)
            raise AssertionError(f"Could not retrieve data from Canvas LMS instance at {target_url}")
        new_items = json.loads(web_response.text)
        current_items += new_items
        if web_response.links.get('next'):
            next_page_url = web_response.links['next'].get('url')
            return self.paginate_through_url(target_url=next_page_url, current_items=current_items)
        return tuple(current_items)


    def paginate_through_url_account_users(self, target_url: str, current_items: List = None) -> Tuple[Dict]:
        if current_items is None:
            current_items = []
        web_response = self.paginated_result_account_users(target_url)
        current_items += json.loads(web_response.text)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if len(current_items)>0:
            lastactive_date = self.get_last_active_date(current_items[len(current_items)-1].get('last_login'))
        while web_response.links.get('next') and lastactive_date >= yesterday:
            next_page_url = web_response.links['next'].get('url')
            web_response = self.paginated_result_account_users(next_page_url)
            current_items += json.loads(web_response.text)
            lastactive_date = self.get_last_active_date(current_items[len(current_items)-1].get('last_login'))
        return tuple(current_items)

    def get_last_active_date(self, last_login):
        if last_login is None:
            return datetime.datetime.strptime("2000-01-01T00:00:00Z", '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')
        return datetime.datetime.strptime(last_login, '%Y-%m-%d' + 'T' + '%H:%M:%S' + 'Z')

    def paginated_result_account_users(self, target_url:str) -> response:
        web_response = self.web_session.get(target_url)
        if web_response.status_code != 200:
            print(web_response)
            raise AssertionError(f"Could not retrieve data from Canvas LMS instance at {CANVAS_API_URL}")
        return web_response

    def get_canvas_account_id_of_current_user(self) -> int:
        web_response = self.web_session.get(f"{CANVAS_API_URL}/users/self")
        account_json = json.loads(web_response.text)
        return int(account_json['id'])

    def get_canvas_accounts(self) -> Tuple[Dict]:
        """Get a list of accounts that the current user can view or manage"""
        url = f"{CANVAS_API_URL}/accounts"
        return self.paginate_through_url(url)

    def get_account_users(self, account_id: int) -> Tuple[Dict]:
        """Get a list of of users associated with specified account"""
        url = f"{CANVAS_API_URL}/accounts/{account_id}/users?sort=last_login&order=desc"
        return self.paginate_through_url_account_users(url)

    def get_user_history(self, canvas_userid: int) -> Dict:
        url = f"{CANVAS_API_URL}/users/{canvas_userid}/history"
        return self.get_single_element_from_url(url)

    def get_course_groups(self, course_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/groups?per_page=100"
        return self.paginate_through_url(url)

    def get_group_users(self, group_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/groups/{group_id}/users?per_page=100"
        return self.paginate_through_url(url)

    def get_course_students(self, course_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/users?enrollment_type[]=student&per_page=100"
        return self.paginate_through_url(url)


    def get_course_students_recently_active(self, course_id) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/recent_students?per_page=100"
        return self.paginate_through_url_account_users(url)

    def get_course_modules(self, course_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/modules?per_page=100"
        return self.paginate_through_url(url)

    def get_finnish_mark_per_student(self, course_id: int, module_id: int, student_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/modules/{module_id}/items?student_id={student_id}&per_page=100"
        return self.paginate_through_url_module_items(url)


    def get_course_module_items(self, course_id: int, module_id: int) -> Tuple[Dict]:
        url = f"{CANVAS_API_URL}/courses/{course_id}/modules/{module_id}/items?per_page=100"
        return self.paginate_through_url(url)

    def get_student_completed_item(self, course_id: int, module_id: int, item_id: int, student_id: int) -> Dict:
        url = f"{CANVAS_API_URL}/courses/{course_id}/modules/{module_id}/items/{item_id}?student_id={student_id}"
        return self.get_single_element_from_url(url)

    def get_student_completed(self, course_id: int, student_id: int) -> Dict:
        url = f"{CANVAS_API_URL}/courses/{course_id}/enrollments?state[]=completed&user_id={student_id}"
        return self.paginate_through_url(url)

    def get_submissions_in_quiz(self, course_id, assignment_id):
        '''Get submissions in a given quiz to access open answer responses'''
        url = f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}/submissions?include[]=submission_history&per_page=100"
        return self.paginate_through_url(url)

    def get_udirdev_account_users(self, account_id: int):
        url = f"{CANVAS_API_URL}/accounts/{account_id}/users?include[]=email&search_term=%40udir%2Edev&per_page=100"
        return self.paginate_through_url(url)

    def delete_user(self, account_id, user_id):
        url = f"{CANVAS_API_URL}/accounts/{account_id}/users/{user_id}"
        web_response = self.web_session.delete(url)
        if web_response.status_code != 200:
            raise AssertionError(f"Could not delete user from Canvas LMS instance at {CANVAS_API_URL}")
