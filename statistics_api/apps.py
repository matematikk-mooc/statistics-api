from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.core import management

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.definitions import DATABASE_REFRESH_MINUTE, DATABASE_REFRESH_HOUR, CANVAS_ACCESS_KEY, CANVAS_DOMAIN, \
    KPAS_API_ACCESS_TOKEN
from statistics_api.definitions import KPAS_URL
from statistics_api.scheduled_tasks.course_enrollment_activity import EnrollmentActivity
from statistics_api.scheduled_tasks.fetch_school_data_from_nsr import get_requests
from statistics_api.scheduled_tasks.fetch_school_data_from_nsr import post_to_kpas


def fetch_course_enrollment():
    api_client = CanvasApiClient()
    courses = api_client.get_courses()
    for course in courses:
        course_enrollment = EnrollmentActivity(graphql_api_url="https://{}/api/graphql".format(CANVAS_DOMAIN),
                                               course_id=course['id'],
                                               access_token=CANVAS_ACCESS_KEY)
        course_enrollment.fetch_enrollment_activity()


def fetch_school_data():
    # TODO: Move this task to Azure Functions etc.
    headers = {"Authorization": "Bearer " + KPAS_API_ACCESS_TOKEN}
    post_to_kpas(path="/run_scheduler", headers=headers)
    get_requests(url=KPAS_URL, path="/run_scheduler")


class StatisticsApiConfig(AppConfig):
    name = 'statistics_api'
    verbose_name = "Statistics API for enrollment at Canvas courses"

    def ready(self):

        def start_scheduler():
            """ run refresh_database at preset hour  """
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                management.call_command,
                args=("pull_course_member_counts_from_canvas",),
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.add_job(
                fetch_course_enrollment,
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.add_job(
                fetch_school_data,
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.start()

        start_scheduler()
