from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from typing import List

from statistics_api.clients.canvas_api_client import CanvasApiClient
from statistics_api.course_info.models import CourseObservation
from statistics_api.course_info.models import Group
from statistics_api.course_info.models import GroupCategory
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict, START_DATE_KEY, END_DATE_KEY, \
    NR_OF_DATES_LIMIT_KEY


@require_http_methods(["GET"])
def course(request: WSGIRequest, course_canvas_id: int):
    url_parameters_dict = get_url_parameters_dict(request)
    start_date, end_date, nr_of_dates_limit = (url_parameters_dict[
                                                   START_DATE_KEY],
                                               url_parameters_dict[
                                                   END_DATE_KEY],
                                               url_parameters_dict[
                                                   NR_OF_DATES_LIMIT_KEY])

    api_client = CanvasApiClient()
    course_metadata = api_client.get_course(course_canvas_id)

    course_observations = CourseObservation.objects.filter(canvas_id=course_canvas_id, date_retrieved__gte=start_date,
                                                           date_retrieved__lte=end_date).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_dates_limit]

    if not course_observations:
        return HttpResponseNotFound("Could not find course with requested ID.")

    json_response = []

    for course_observation in course_observations:
        course_group_categories = GroupCategory.objects.filter(course_id=course_observation.id)
        groups = []
        for group_category in course_group_categories:
            groups += Group.objects.filter(group_category_id=group_category.id)

        groups_dict = {}
        for group_category in course_group_categories:
            groups_in_category: List[dict] = list(
                map(lambda g: {"canvas_id": g.canvas_id, "name": g.name, "member_count": g.members_count},
                    (group for group in groups if
                     group.group_category_id == group_category.id))
            )

            category_member_count: int = sum(group['member_count'] for group in groups_in_category)

            group_category_info = {
                "canvas_id": group_category.canvas_id,
                "member_count": category_member_count,
                "groups": groups_in_category,
            }

            groups_dict[group_category.name] = group_category_info

        course_observation_json = {
            "date": course_observation.date_retrieved,
            "enrollment_count": course_metadata["total_students"],
            "group_categories": groups_dict
        }

        json_response.append(course_observation_json)

    return JsonResponse({"Result": json_response})


@require_http_methods(["GET"])
def course_count(_: WSGIRequest, course_canvas_id: int):
    api_client = CanvasApiClient()
    course_metadata = api_client.get_course(course_canvas_id)

    json_response = []
    course_observation_count = {
        "start_date": course_metadata["start_at"],
        "enrollment_count": course_metadata["total_students"]
    }

    json_response.append(course_observation_count)

    return JsonResponse({"Result": json_response})
