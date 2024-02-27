# import subprocess

# from django.test.runner import DiscoverRunner as BaseRunner


# class MyMixinRunner(object):
#     def setup_databases(self, *args, **kwargs):
#         temp_return = super(MyMixinRunner, self).setup_databases(*args, **kwargs)

#         # Instead of letting Python initialize the test database, initialize it manually before running the tests,
#         # and the run the tests with "--keepdb" flag.
#         #subprocess.run([f"mysql --host=127.0.0.1 --port={DB_PORT} -uroot -p{MYSQL_ROOT_PASSWORD} test_{DB_DATABASE} < {TEST_DATABASE_FILE_PATH}"], shell=True)
#         return temp_return


# class MyTestRunner(MyMixinRunner, BaseRunner):
#     pass
