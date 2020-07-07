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
                args=("do_all_scheduled_maintenance_jobs",),
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.start()

        start_scheduler()
