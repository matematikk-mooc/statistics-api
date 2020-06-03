from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from statistics_api.definitions import DATABASE_REFRESH_MINUTE, DATABASE_REFRESH_HOUR


class StatisticsApiConfig(AppConfig):
    name = 'statistics_api'
    verbose_name = "Statistics API for enrollment at Canvas courses"

    def post_migration_callback(self, sender, **kwargs):
        from statistics_api.refresh_database import refresh_database
        refresh_database()

    def ready(self):
        from statistics_api.refresh_database import refresh_database

        def start_scheduler():
            """ run refresh_database at preset hour  """
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                refresh_database,
                max_instances=1,
                replace_existing=False,
                trigger="cron",
                minute=DATABASE_REFRESH_MINUTE,
                hour=DATABASE_REFRESH_HOUR,
            )
            scheduler.start()

        start_scheduler()

        post_migrate.connect(self.post_migration_callback, sender=self)
