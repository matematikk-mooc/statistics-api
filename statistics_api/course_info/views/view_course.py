from django.http import JsonResponse, HttpResponseNotFound

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.course_info.models import CourseObservation
from statistics_api.course_info.models import Group
from statistics_api.course_info.models import GroupCategory
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict
from rest_framework.decorators import api_view
from statistics_api.utils.url_parameter_parser import START_DATE_KEY, END_DATE_KEY, NR_OF_DATES_LIMIT_KEY


# Create your views here.

@api_view(['GET'])
def course(request, course_canvas_id):
    url_parameters_dict = get_url_parameters_dict(request)
    start_date = url_parameters_dict.get(START_DATE_KEY)
    end_date = url_parameters_dict.get(END_DATE_KEY)
    nr_of_dates_limit = url_parameters_dict.get(NR_OF_DATES_LIMIT_KEY)

    api_client = CanvasApiClient()
    try:
        course_metadata = api_client.get_course(course_canvas_id)
    except Exception as e:
        return HttpResponseNotFound(f"Could not find course with requested ID. Error: {e}")

    course_observations = CourseObservation.objects.filter(
        canvas_id=course_canvas_id,
        date_retrieved__range=(start_date, end_date)
    ).order_by('-date_retrieved')[:nr_of_dates_limit]

    if not course_observations:
        return HttpResponseNotFound("Could not find course observations for the requested period.")

    json_response = build_json_response(course_observations, course_metadata)

    return JsonResponse({"Result": json_response})

@api_view(['GET'])
def course_count(request, course_canvas_id):
    api_client = CanvasApiClient()
    try:
        course_metadata = api_client.get_course(course_canvas_id)
    except Exception as e:
        return JsonResponse({"error": f"Could not find course with requested ID. Error: {e}"}, status=404)

    json_response = [{
        "start_date": course_metadata.get("start_at"),
        "enrollment_count": course_metadata.get("total_students")
    }]

    return JsonResponse({"Result": json_response})


def build_json_response(course_observations, course_metadata):
    json_response = []

    for course_observation in course_observations:
        group_categories = GroupCategory.objects.filter(course_id=course_observation.id)
        groups_dict = {}

        for group_category in group_categories:
            groups = Group.objects.filter(group_category_id=group_category.id)
            groups_in_category = [{
                "canvas_id": group.canvas_id,
                "name": group.name,
                "member_count": group.members_count
            } for group in groups]

            category_member_count = sum(group['member_count'] for group in groups_in_category)

            groups_dict[group_category.name] = {
                "canvas_id": group_category.canvas_id,
                "member_count": category_member_count,
                "groups": groups_in_category
            }

        course_observation_json = {
            "date": course_observation.date_retrieved,
            "enrollment_count": course_metadata.get("total_students", 0),
            "group_categories": groups_dict
        }

        json_response.append(course_observation_json)

    return json_response
