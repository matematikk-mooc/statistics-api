import asyncio
import datetime

import arrow
import requests
from python_graphql_client import GraphqlClient

from statistics_api.definitions import CANVAS_ACCESS_KEY, CA_FILE_PATH


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


def filter_enrollment_activity_by_date(data):
    """
    Filter enrollment activity
    :param data: Dict
    :return:
    """
    edges = data["data"]["course"]["enrollmentsConnection"]["edges"]
    active_users_yesterday = list(filter(compare_date, edges))
    return len(active_users_yesterday)


class EnrollmentActivity(object):
    def __init__(self, access_token: str, graphql_api_url: str, course_id: str) -> None:
        self.access_token = access_token
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
        while result['data']['course']['enrollmentsConnection']['pageInfo']['hasNextPage']:
            after_cursor = result['data']['course']['enrollmentsConnection']['pageInfo']['endCursor']
            self.variables["after"] = after_cursor
            loop = asyncio.get_event_loop()
            try:
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

        self.ingest_to_kpas(enrollment_activity)

    def ingest_to_kpas(self, data):
        """
        Ingest enrollment activity date to kpas
        :param data:
        :return:
        """
        try:
            r = self.web_session.post('https://kpaslocal.example.com/api/user_activity/', data=data)
        except Exception as err:
            print("EnrollmentActivity error while ingesting into kpas : {0}".format(err))
            raise
        print(r.text)
