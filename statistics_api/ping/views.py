import os
import datetime

import sentry_sdk

from django.http import JsonResponse

from rest_framework.decorators import api_view

from statistics_api.total_students.models import TotalStudents
from statistics_api.total_students.views import TotalStudentsSerializer
from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.clients.matomo_api_client import MatomoApiClient

@api_view(('GET',))
def ping_view(request):
    app_version = os.getenv('GIT_COMMIT') if os.getenv('GIT_COMMIT') else "1.0.0"
    response_data = {
        "error": False,
        "statusCode": 200,
        "result": {
            "version": app_version,
            "database": False,
            "integrations": {
                "canvas": False,
                "matomo": False,
            }
        }
    }

    try:
        queryset = TotalStudents.objects.filter(course_id=360, date=datetime.date.today())
        TotalStudentsSerializer(queryset, many=True)
        response_data["result"]["database"] = True
    except Exception as e:
        sentry_sdk.capture_exception(e)
        response_data["error"] = True
        response_data["statusCode"] = 500
        response_data["result"]["database"] = False

    try:
        canvas_api_client = CanvasApiClient()
        canvas_api_client.get_course(canvas_course_id=360)
        response_data["result"]["integrations"]["canvas"] = True
    except Exception as e:
        sentry_sdk.capture_exception(e)
        response_data["error"] = True
        response_data["statusCode"] = 500
        response_data["result"]["integrations"]["canvas"] = False

    try:
        matomo_api_client = MatomoApiClient()
        matomo_api_client.get_matomo_page_statistics()
        response_data["result"]["integrations"]["matomo"] = True
    except Exception as e:
        sentry_sdk.capture_exception(e)
        response_data["error"] = True
        response_data["statusCode"] = 500
        response_data["result"]["integrations"]["matomo"] = False

    return JsonResponse(response_data, status=response_data["statusCode"])
