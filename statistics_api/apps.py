from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.core import management
from statistics_api.definitions import DATABASE_REFRESH_MINUTE, DATABASE_REFRESH_HOUR


class StatisticsApiConfig(AppConfig):
    name = 'statistics_api'
    verbose_name = "Statistics API for enrollment at Canvas courses"

    def ready(self):

        # TODO: Move these scheduled task to Azure Functions etc.
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
                management.call_command,
                args=("fetch_course_enrollment_and_post_to_kpas",),
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.add_job(
                management.call_command,
                args=("trigger_scheduling_of_kpas_job",),
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.start()

        start_scheduler()
