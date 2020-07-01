from collections import defaultdict

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods

from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory
from statistics_api.utils.query_maker import get_group_category_observations_between_dates_query, \
    get_groups_by_group_category_ids_query
from statistics_api.utils.url_parameter_parser import get_url_parameters


@require_http_methods(["GET"])
def group_category(request: WSGIRequest, group_category_canvas_id: int):
    start_date, end_date, _, nr_of_dates_limit = get_url_parameters(request)

    group_category_observations_between_dates_query: str = get_group_category_observations_between_dates_query()
    group_categories = GroupCategory.objects.raw(
        group_category_observations_between_dates_query,
        [group_category_canvas_id, start_date, end_date, nr_of_dates_limit])

    json_response = []

    groups_by_group_category_ids_query = get_groups_by_group_category_ids_query(
        tuple([int(g_cat.pk) for g_cat in group_categories]))

    groups = Group.objects.raw(groups_by_group_category_ids_query)

    date_to_groups_mapping = defaultdict(list)

    for group in groups:
        date_to_groups_mapping[group.date_retrieved].append(group)

    for date in date_to_groups_mapping.keys():
        groups = date_to_groups_mapping.get(date)
        group_dicts = [group.to_dict() for group in groups]
        group_category_json = {
            "date": date,
            "groups": group_dicts
        }

        json_response.append(group_category_json)

    return JsonResponse({"Result": json_response})


@require_http_methods(["GET"])
def group_category_count(request: WSGIRequest, group_category_canvas_id: int):

    start_date, end_date, _, nr_of_dates_limit = get_url_parameters(request)

    group_category_observations_between_dates_query: str = get_group_category_observations_between_dates_query()
    group_categories = GroupCategory.objects.raw(
        group_category_observations_between_dates_query,
        [group_category_canvas_id, start_date, end_date, nr_of_dates_limit])

    json_response = []

    for group_category in group_categories:
        groups = Group.objects.filter(group_category=group_category.pk)
        group_category_json = {
            "date": group_category.date_retrieved,
            "nr_of_groups_in_category": len(groups)
        }

        json_response.append(group_category_json)

    return JsonResponse({"Result": json_response})
