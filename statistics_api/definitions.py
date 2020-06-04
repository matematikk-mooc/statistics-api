from distutils import util
import os

from sqlalchemy.ext.declarative import declarative_base

ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"

CA_FILE_NAME = os.getenv("CA_FILE_NAME")
CA_FILE_PATH = ROOT_DIR + f"../{CA_FILE_NAME}" if CA_FILE_NAME else None

CANVAS_DOMAIN = str(os.getenv("CANVAS_DOMAIN")).strip("'\"")
CANVAS_API_URL = f"https://{CANVAS_DOMAIN}/api/v1"
CANVAS_ACCESS_KEY = str(os.getenv("CANVAS_ACCESS_KEY")).strip("'\"")
CANVAS_ACCOUNT_ID = str(os.getenv("CANVAS_ACCOUNT_ID")).strip("'\"")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

# NB! Hour and mintue of the day are in UTC
DATABASE_REFRESH_HOUR = str(os.getenv("DATABASE_REFRESH_HOUR")).zfill(2) if os.getenv("DATABASE_REFRESH_HOUR") else "03"
DATABASE_REFRESH_MINUTE = str(os.getenv("DATABASE_REFRESH_MINUTE")).zfill(2) if os.getenv(
    "DATABASE_REFRESH_MINUTE") else "00"

MYSQL_VARCHAR_DEFAULT_LENGTH = 255
MYSQL_CASCADE = "CASCADE"
Base = declarative_base()
STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"

DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DJANGO_DEBUG = bool(util.strtobool(os.getenv("DJANGO_DEBUG"))) if os.getenv("DJANGO_DEBUG") is not None else False
DJANGO_ALLOWED_HOSTS = [s.strip() for s in os.getenv("DJANGO_ALLOWED_HOSTS").split(',')] if os.getenv(
    "DJANGO_ALLOWED_HOSTS") else []
