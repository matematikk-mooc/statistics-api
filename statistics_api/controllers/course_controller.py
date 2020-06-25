from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory


@require_http_methods(["GET"])
def course(request: WSGIRequest, course_canvas_id: int):
    nr_of_most_recent_dates: int = int(request.GET.get('nr_of_dates', 1))
    course_observations = CourseObservation.objects.filter(canvas_id=course_canvas_id).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_most_recent_dates]

    json_response = []

    for course_observation in course_observations:
        child_group_categories = GroupCategory.objects.filter(course_id=course_observation.id)
        child_groups = []
        for group_category in child_group_categories:
            child_groups += Group.objects.filter(group_category_id=group_category.id)

        total_students = sum([group.members_count for group in child_groups])

        group_category_names = [group_category.name for group_category in child_group_categories]
        group_category_member_counts = []
        for group_category in child_group_categories:
            group_category_member_counts.append(len([group for group in child_groups if group.group_category_id == group_category.id]))

        groups_dict = dict(zip(group_category_names, group_category_member_counts))

        course_observation_json = {
            "date": course_observation.date_retrieved,
            "antallBrukere": total_students,
            "groups": groups_dict
        }

        json_response.append(course_observation_json)

    return JsonResponse({"Result": json_response})


@require_http_methods(["GET"])
def course_count(request: WSGIRequest, course_canvas_id: int):
    nr_of_most_recent_dates: int = int(request.GET.get('nr_of_dates', 1))
    course_observations = CourseObservation.objects.filter(canvas_id=course_canvas_id).order_by(f"-{CourseObservation.date_retrieved.field.name}")[:nr_of_most_recent_dates]

    json_response = []

    for course_observation in course_observations:
        child_group_categories = GroupCategory.objects.filter(course_id=course_observation.id)
        child_groups = []
        for group_category in child_group_categories:
            child_groups += Group.objects.filter(group_category_id=group_category.id)

        total_students = sum([group.members_count for group in child_groups])

        course_observation_count = {
            "date": course_observation.date_retrieved,
            "antallBrukere": total_students
        }

        json_response.append(course_observation_count)

    return JsonResponse({"Result": json_response})
