import logging
import sys
import logging
from datetime import date, timedelta
import requests
from django.core.management import BaseCommand
from python_graphql_client import GraphqlClient

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import CANVAS_DOMAIN, CANVAS_ACCESS_KEY, CA_FILE_PATH, CANVAS_ACCOUNT_ID
from statistics_api.course_registrations.models import DailyRegistrations

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger()

class Command(BaseCommand):
    help = """Retrieves per-course group membership registrations for all courses administrated by the Canvas account ID
            set in environment settings."""

    def handle(self, *args, **options):
        logger.info("Starting pulling group membership registrations from Canvas")
        try:
            api_client = CanvasApiClient()
            canvas_account_id: int = CANVAS_ACCOUNT_ID if CANVAS_ACCOUNT_ID else api_client.get_canvas_account_id_of_current_user()
            courses = api_client.get_courses(138)
            for course in courses:
                if(course['id'] == 360 or course['total_students'] == 0):
                    continue
                course_id = course['id']
                try:
                    registrations = Registrations(graphql_api_url="https://{}/api/graphql".format(CANVAS_DOMAIN),
                        course_id=course_id, access_token=CANVAS_ACCESS_KEY)
                    registrations.fetch_group_registrations(course_id=course_id)
                    registrations.fetch_course_registrations(course_id=course_id)

                except Exception as e:
                    logger.error("Error processing course ID %s: %s", course_id, str(e))
            logger.info("Finished pulling group membership registrations from Canvas")
        except Exception as e:
            logger.error("Error fetching courses from Canvas: %s", str(e))

class Registrations(object):
    def __init__(self, access_token: str, graphql_api_url: str, course_id: int) -> None:
        self.access_token = access_token
        self.course_id = course_id
        self.headers = {'Authorization': 'Bearer ' + self.access_token,
                        "Content-Type": "application/json"}
        self.variables = {"courseId": self.course_id, "firstCourses": 500, "firstGroups": 10}
        self.group_query = """
            query GroupMembershipQuery ($courseId: ID!, $firstGroups: Int, $afterGroups: String) {
                course(id: $courseId) {
                    groupsConnection (first: $firstGroups, after: $afterGroups) {
                        edges {
                            node {
                                _id
                                name
                                membersConnection {
                                    edges {
                                        node {
                                            createdAt
                                            state
                                        }

                                    }
                                }
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
        self.course_query = """
            query CourseMembershipQuery ($courseId: ID!, $firstCourses: Int, $after: String) {
                course(id: $courseId) {
                    enrollmentsConnection(first: $firstCourses, after: $after) {
                        edges {
                            node {
                                createdAt
                                state
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


    def fetch_group_registrations(self, course_id: int):
        """
        Fetch group registrations for a given course and add to database
        :return:
        """
        yesterday = date.today() - timedelta(1)
        try:
            result = self.client.execute(query=self.group_query, variables=self.variables)
            registrations_to_add = []

            for group in result.get("data", {}).get("course", {}).get("groupsConnection", {}).get("edges", []):
                registrered_yesterday = self.filter_group_registrations_on_date(group, yesterday)
                if registrered_yesterday > 0:
                    registrations_to_add.append(DailyRegistrations(
                        group_id=group.get("node", {}).get("_id"),
                        course_id=course_id,
                        group_name=group.get("node", {}).get("name"),
                        registrations=registrered_yesterday,
                        date=yesterday
                    ))

            while result['data']['course']['groupsConnection']['pageInfo']['hasNextPage']:
                after_cursor = result['data']['course']['groupsConnection']['pageInfo']['endCursor']
                self.variables["afterGroups"] = after_cursor
                try:
                    result = self.client.execute(query=self.group_query, variables=self.variables)
                    for group in result.get("data", {}).get("course", {}).get("groupsConnection", {}).get("edges", []):
                        registrered_yesterday = self.filter_group_registrations_on_date(group, yesterday)
                        if registrered_yesterday > 0:
                            registrations_to_add.append(DailyRegistrations(
                                group_id=group.get("node", {}).get("_id"),
                                course_id=course_id,
                                group_name=group.get("node", {}).get("name"),
                                registrations=registrered_yesterday,
                                date=yesterday
                            ))
                except Exception as err:
                    logger.error("GroupRegistrations error: {0}".format(err))
                    raise

            DailyRegistrations.objects.bulk_create(registrations_to_add)


        except Exception as err:
            logger.error("GroupRegistrations error : {0}".format(err))



    def filter_group_registrations_on_date(self, data, yesterday):
        """
        Filter group registrations on date
        :param data: Dict
        :return: length of registrations
        """
        edges = data.get("node", {}).get("membersConnection", {}).get("edges", [])
        registrered_yesterday = [edge for edge in edges if self.compare_date(edge.get("node", {}), yesterday)]

        return len(registrered_yesterday)


    def fetch_course_registrations(self, course_id):
        """
        Fetch course registrations
        :return:
        """
        yesterday = date.today() - timedelta(1)
        try:
            result = self.client.execute(query=self.course_query, variables=self.variables)

            edges =  result.get("data", {}).get("course", {}).get("enrollmentsConnection", {}).get("edges", [])
            registrered_yesterday = [edge for edge in edges if self.compare_date(edge.get("node", {}), yesterday)]
            registrations_count = len(registrered_yesterday)

            while result['data']['course']['enrollmentsConnection']['pageInfo']['hasNextPage']:
                after_cursor = result['data']['course']['enrollmentsConnection']['pageInfo']['endCursor']
                self.variables["after"] = after_cursor
                try:
                    result = self.client.execute(query=self.course_query, variables=self.variables)
                    edges =  result.get("data", {}).get("course", {}).get("enrollmentsConnection", {}).get("edges", [])
                    registrered_yesterday = [edge for edge in edges if self.compare_date(edge.get("node", {}), yesterday)]
                    registrations_count += len(registrered_yesterday)
                except Exception as err:
                    logger.error("CourseRegistrations error: {0}".format(err))
                    raise

            if registrations_count > 0:
                DailyRegistrations.objects.create(
                    course_id=course_id,
                    group_id=course_id,
                    group_name="Course",
                    registrations=registrations_count,
                    date=yesterday
                )
        except Exception as err:
            logger.error("CourseRegistrations error : {0}".format(err))


    def compare_date(self, node, yesterday):
        """
        If createdAt time is in last 24 , then return true
        :param node: Membership object
        :return: boolean
        """
        createdAt = node.get('createdAt')
        if not createdAt:
            return False
        yesterday = date.today() - timedelta(1)
        createdAt = date.fromisoformat(createdAt.split("T")[0])
        return createdAt >= yesterday
