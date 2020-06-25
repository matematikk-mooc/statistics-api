from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory

GROUP_CATEGORY_ID = f"{GroupCategory._meta.db_table}.{GroupCategory._meta.pk.attname}"
GROUP_CATEGORY_CANVAS_ID = f"{GroupCategory._meta.db_table}.{GroupCategory.canvas_id.field.name}"
COURSE_OBSERVATION_ID = f"{CourseObservation._meta.db_table}.{CourseObservation._meta.pk.attname}"
DATE_RETRIEVED = str(CourseObservation.date_retrieved.field.name)
GROUP_CATEGORY_COURSE_FK = str(GroupCategory.course.field.attname)


@require_http_methods(["GET"])
def group_category(request: WSGIRequest, group_category_canvas_id: int):
    nr_of_most_recent_dates: int = int(request.GET.get('nr_of_dates', 1))

    group_categories = GroupCategory.objects.raw(
        f"""SELECT {GROUP_CATEGORY_ID}, {DATE_RETRIEVED} FROM {GroupCategory._meta.db_table}
        LEFT JOIN {CourseObservation._meta.db_table} ON {GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
        WHERE {GROUP_CATEGORY_CANVAS_ID} = %s
        ORDER BY {DATE_RETRIEVED} DESC LIMIT %s""",
        [group_category_canvas_id, nr_of_most_recent_dates])

    json_response = []

    for group_category in group_categories:
        groups = Group.objects.filter(group_category=group_category.pk)
        group_dicts = [group.to_dict() for group in groups]
        group_category_json = {
            "date": group_category.date_retrieved,
            "groups": group_dicts
        }

        json_response.append(group_category_json)

    return JsonResponse({"Result": json_response})


@require_http_methods(["GET"])
def group_category_count(request: WSGIRequest, group_category_canvas_id: int):

    nr_of_most_recent_dates: int = int(request.GET.get('nr_of_dates', 1))
    group_categories = GroupCategory.objects.raw(
        f"""SELECT {GROUP_CATEGORY_ID}, {DATE_RETRIEVED} FROM {GroupCategory._meta.db_table}
            LEFT JOIN {CourseObservation._meta.db_table} ON {GROUP_CATEGORY_COURSE_FK} = {COURSE_OBSERVATION_ID}
            WHERE {GROUP_CATEGORY_CANVAS_ID} = %s
            ORDER BY {DATE_RETRIEVED} DESC LIMIT %s""",
        [group_category_canvas_id, nr_of_most_recent_dates])

    json_response = []

    for group_category in group_categories:
        groups = Group.objects.filter(group_category=group_category.pk)
        group_category_json = {
            "date": group_category.date_retrieved,
            "nr_of_groups_in_category": len(groups)
        }

        json_response.append(group_category_json)

    return JsonResponse({"Result": json_response})
