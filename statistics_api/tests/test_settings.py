from statistics_api.settings import *

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_REFERRER_POLICY = False
if os.environ.get('TESTS_WITHOUT_MIGRATIONS', False):
    MIGRATION_MODULES = {
        app.split('.')[-1]: None for app in INSTALLED_APPS
    }