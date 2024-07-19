import os
import socket
from distutils import util
import netifaces as ni
from sqlalchemy.ext.declarative import declarative_base

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        finally:
            s.close()
        return ip_address
    except Exception as e:
        print(f"Error obtaining IP address: {e}")
        return None

####    START OF ENVIRONMENT VARIABLES  ####

ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"

CA_FILE_NAME = os.getenv("CA_FILE_NAME")
CA_FILE_PATH = ROOT_DIR + f"../{CA_FILE_NAME}" if CA_FILE_NAME else None

CANVAS_DOMAIN = str(os.getenv("CANVAS_DOMAIN")).strip("'\"")
CANVAS_API_URL = f"https://{CANVAS_DOMAIN}/api/v1"
CANVAS_ACCESS_KEY = str(os.getenv("CANVAS_ACCESS_KEY")).strip("'\'").strip('\"')
CANVAS_ACCOUNT_ID = os.getenv("CANVAS_ACCOUNT_ID")

KPAS_DOMAIN = str(os.getenv("KPAS_DOMAIN")).strip("'\"") if os.getenv("KPAS_DOMAIN") else None
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

ip = get_ip_address()
if ip:
    allowed_hosts.append(ip)

allowed_hosts.append("0.0.0.0")
allowed_hosts.append("127.0.0.1")
allowed_hosts.append("localhost")

DJANGO_ALLOWED_HOSTS = allowed_hosts

BUGSNAG_API_KEY = os.getenv("BUGSNAG_API_KEY")

MATOMO_ACCESS_KEY = os.getenv("MATOMO_ACCESS_KEY")
MATOMO_API_URL = "https://statistik.digilaer.no/index.php"

####    END OF ENVIRONMENT VARIABLES  ####


MYSQL_VARCHAR_DEFAULT_LENGTH = 255
MYSQL_CASCADE = "CASCADE"
Base = declarative_base()
STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"
