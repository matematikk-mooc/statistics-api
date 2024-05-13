import os
from distutils import util
import netifaces as ni
from sqlalchemy.ext.declarative import declarative_base

####    START OF ENVIRONMENT VARIABLES  ####

ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"

CA_FILE_NAME = os.getenv("CA_FILE_NAME")
CA_FILE_PATH = ROOT_DIR + f"../{CA_FILE_NAME}" if CA_FILE_NAME else None

CANVAS_DOMAIN = str(os.getenv("CANVAS_DOMAIN")).strip("'\"")
CANVAS_API_URL = f"https://{CANVAS_DOMAIN}/api/v1"
CANVAS_ACCESS_KEY = str(os.getenv("CANVAS_ACCESS_KEY")).strip("'\'").strip('\"')
CANVAS_ACCOUNT_ID = os.getenv("CANVAS_ACCOUNT_ID")

KPAS_DOMAIN = str(os.getenv("KPAS_DOMAIN")).strip("'\"") if os.getenv("KPAS_DOMAIN") else None
if os.getenv("ENVIRONMENT") == "dev":
    KPAS_API_URL = f"http://{KPAS_DOMAIN}/api" if KPAS_DOMAIN else None
else:
    KPAS_API_URL = f"https://{KPAS_DOMAIN}/api" if KPAS_DOMAIN else None
KPAS_NSR_API_URL = f"{KPAS_API_URL}/nsr" if KPAS_API_URL else None
KPAS_API_ACCESS_TOKEN = os.getenv("KPAS_API_ACCESS_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

# NB! Hour and minute of the day are in UTC
DATABASE_REFRESH_HOUR = str(os.getenv("DATABASE_REFRESH_HOUR")).zfill(2) if os.getenv("DATABASE_REFRESH_HOUR") else "03"
DATABASE_REFRESH_MINUTE = str(os.getenv("DATABASE_REFRESH_MINUTE")).zfill(2) if os.getenv(
    "DATABASE_REFRESH_MINUTE") else "00"

DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DJANGO_DEBUG = bool(util.strtobool(os.getenv("DJANGO_DEBUG"))) if os.getenv("DJANGO_DEBUG") is not None else False
allowed_hosts = [s.strip() for s in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(',')]
if not allowed_hosts:
    allowed_hosts = ["*"]

ni.ifaddresses('eth0')
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

allowed_hosts.append(ip)

DJANGO_ALLOWED_HOSTS = allowed_hosts

BUGSNAG_API_KEY = os.getenv("BUGSNAG_API_KEY")

MATOMO_ACCESS_KEY = os.getenv("MATOMO_ACCESS_KEY")
MATOMO_API_URL = "https://statistik.digilaer.no/index.php"

####    END OF ENVIRONMENT VARIABLES  ####


MYSQL_VARCHAR_DEFAULT_LENGTH = 255
MYSQL_CASCADE = "CASCADE"
Base = declarative_base()
STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Codes denoting various levels of teacher enrollment percentages. E.g., a school with enrollment_percentage_category
# '0' has exactly 0 % course enrollment among teachers, whereas a school with enrollment_percentage_category '1' has
# (0-20] % course enrollment among teachers.
PERCENTAGE_INTERVALS = {
    0: 0,
    1: 20,
    2: 40,
    3: 60,
    4: 80,
    5: 100
}

CATEGORY_CODES = [k for k in PERCENTAGE_INTERVALS.keys()]
CATEGORY_CODES.sort()

TOO_FEW_TEACHERS_CODE = 99
TOO_FEW_TEACHERS_CUTOFF = 5


enrollment_percentage_category_codes = {CATEGORY_CODES[0]: f"e = {PERCENTAGE_INTERVALS[CATEGORY_CODES[0]]} %"}

for i in range(len(CATEGORY_CODES)-1):
    category_code = CATEGORY_CODES[i+1]
    previous_category_code = CATEGORY_CODES[i]
    lower_bound = PERCENTAGE_INTERVALS[previous_category_code]
    upper_bound = PERCENTAGE_INTERVALS[category_code]
    enrollment_percentage_category_codes.update({category_code: f"{lower_bound} % < e <= {upper_bound} %"})

CATEGORY_CODE_INFORMATION_DICT = {
    "info":
        {"description": "Category codes denoting intervals of enrollment percentage. e = course enrollment percentage"}
}

CATEGORY_CODE_INFORMATION_DICT["info"].update({"category_codes": enrollment_percentage_category_codes})