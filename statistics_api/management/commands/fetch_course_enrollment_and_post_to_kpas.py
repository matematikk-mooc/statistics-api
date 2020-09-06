import asyncio
import datetime
import logging
import sys
from logging import Logger

import arrow
import requests
from django.core.management import BaseCommand
from python_graphql_client import GraphqlClient

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.clients.kpas_client import KpasClient
from statistics_api.definitions import CANVAS_DOMAIN, CANVAS_ACCESS_KEY, CA_FILE_PATH, CANVAS_ACCOUNT_ID
from statistics_api.enrollment_activity.models import EnrollmentActivity as EnrollmentActivityModel


class Command(BaseCommand):
    help = """Retrieves per-course enrollment activity for all courses administrated by the Canvas account ID
            set in environment settings."""

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        api_client = CanvasApiClient()
        canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
        courses = api_client.get_courses(canvas_account_id=canvas_account_id)
        for course in courses:
            course_enrollment = EnrollmentActivity(graphql_api_url="https://{}/api/graphql".format(CANVAS_DOMAIN),
                                                   course_id=int(course['id']),
                                                   access_token=CANVAS_ACCESS_KEY, logger=logger)
            course_enrollment.fetch_enrollment_activity()


class EnrollmentActivity(object):
    def __init__(self, access_token: str, graphql_api_url: str, course_id: int, logger: Logger) -> None:
        self.logger = logger
        # most_recent_course_observations = get_n_most_recent_course_observations(course_canvas_id=course_id, n=1)
        # if not most_recent_course_observations:
        #     raise AssertionError(f"Could not find observation of course with Canvas LMS ID {course_id}.")
        # most_recent_course_observation = most_recent_course_observations[0]
        # self.total_nr_of_students_for_course = compute_total_nr_of_students_for_course_observation(
        #     most_recent_course_observation.pk)
        self.access_token = access_token
        self.kpas_client = KpasClient()
        self.course_id = course_id
        self.headers = {'Authorization': 'Bearer ' + self.access_token,
                        "Content-Type": "application/json"}
        self.variables = {"courseId": self.course_id, "first": 500}
        self.query = """
                    query courseEnrollment($courseId: ID!, $first: Int) {
                      course(id: $courseId) {
                        name
                        enrollmentsConnection(first: $first){
                          edges{
                            node{
                              lastActivityAt
                              type
                            }
                          cursor
                          }
                          pageInfo {
                            endCursor
                            hasNextPage
                          }
                        }
                      }
                    }
                """
        self.client = GraphqlClient(endpoint=graphql_api_url, headers=self.headers)
        self.web_session = requests.Session()
        self.web_session.headers.update({
            "Authorization": f"Bearer {CANVAS_ACCESS_KEY}"
        })

        self.web_session.verify = CA_FILE_PATH

    def fetch_enrollment_activity(self):
        """
        Fetch enrollment activity for a given course and ingest into kpas-api
        :return:
        """
        active_users_count = 0
        enrollment_activity = {}
        try:
            result = self.client.execute(query=self.query, variables=self.variables)
        except Exception as err:
            print("EnrollmentActivity error : {0}".format(err))
            raise
        active_users_count += filter_enrollment_activity_by_date(result)
        second_query = """
            query courseEnrollment($courseId: ID!, $first: Int, $after: String) {
              course(id: $courseId) {
                name
                enrollmentsConnection(first: $first, after: $after){
                  edges{
                    node{
                      lastActivityAt
                      type
                    }
                  cursor
                  }
                  pageInfo {
                    endCursor
                    hasNextPage
                  }
                }
              }
            }
        """
        # loop while pagination has next page
        checked_nodes: int = 0

        while result['data']['course']['enrollmentsConnection']['pageInfo']['hasNextPage']:
            checked_nodes += len(result['data']['course']['enrollmentsConnection']['edges'])
            # self.logger.info(f"Checked activity for {checked_nodes} out of {self.total_nr_of_students_for_course}")
            after_cursor = result['data']['course']['enrollmentsConnection']['pageInfo']['endCursor']
            self.variables["after"] = after_cursor
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.client.execute_async(query=second_query, variables=self.variables))
                active_users_count += filter_enrollment_activity_by_date(result)
            except Exception as err:
                print("EnrollmentActivity error : {0}".format(err))
                raise

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        enrollment_activity['activity_date'] = yesterday
        enrollment_activity['active_users_count'] = active_users_count
        enrollment_activity['course_id'] = self.course_id
        enrollment_activity['course_name'] = result['data']['course']['name']
        self.logger.info(f"saving {enrollment_activity} to DB")

        created_enrollment_object = EnrollmentActivityModel(
            course_id=enrollment_activity['course_id'],
            course_name=enrollment_activity['course_name'],
            active_users_count=enrollment_activity['active_users_count'],
            activity_date=enrollment_activity['activity_date']
        )
        created_enrollment_object.save()
        self.logger.info(f"{created_enrollment_object} created in DB")


def filter_enrollment_activity_by_date(data):
    """
    Filter enrollment activity
    :param data: Dict
    :return:
    """
    edges = data["data"]["course"]["enrollmentsConnection"]["edges"]
    active_users_yesterday = list(filter(compare_date, edges))
    return len(active_users_yesterday)


def compare_date(node):
    """
    If lastActivityAt time is in last 24 , then return true
    :param node: Enrollment object
    :return: boolean
    """
    if not node["node"]['lastActivityAt']:
        return False
    yesterday = arrow.utcnow().shift(days=-1)
    last_activity_at = arrow.get(node["node"]['lastActivityAt'])
    return last_activity_at >= yesterday
