from django.core.management import call_command
from django.test.runner import DiscoverRunner as BaseRunner

from statistics_api.definitions import TEST_DATABASE_JSON_FILE_PATH


class MyMixinRunner(object):
    def setup_databases(self, *args, **kwargs):
        temp_return = super(MyMixinRunner, self).setup_databases(*args, **kwargs)
        call_command('loaddata', TEST_DATABASE_JSON_FILE_PATH, verbosity=0)
        return temp_return


class MyTestRunner(MyMixinRunner, BaseRunner):
    pass
