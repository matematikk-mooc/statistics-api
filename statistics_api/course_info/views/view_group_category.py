
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import F, Count
from collections import defaultdict
from statistics_api.utils.url_parameter_parser import get_url_parameters_dict
from statistics_api.course_info.models import Group, GroupCategory
from statistics_api.utils.url_parameter_parser import START_DATE_KEY, END_DATE_KEY, NR_OF_DATES_LIMIT_KEY, AGGREGATED
from rest_framework.decorators import api_view

@api_view(['GET'])
def group_category(request, group_category_canvas_id):
    url_parameters_dict = get_url_parameters_dict(request)
    start_date = url_parameters_dict.get(START_DATE_KEY)
    end_date = url_parameters_dict.get(END_DATE_KEY)
    nr_of_dates_limit = url_parameters_dict.get(NR_OF_DATES_LIMIT_KEY)
    aggregated = url_parameters_dict.get(AGGREGATED)

    if not all([start_date, end_date, nr_of_dates_limit]):
        return HttpResponseBadRequest("Missing required parameters")

    group_categories = get_group_categories_between_dates(group_category_canvas_id, start_date, end_date, nr_of_dates_limit)

    json_response = []
    group_ids = [group_category.pk for group_category in group_categories]

    if aggregated is None:
        groups = get_groups_by_group_category_ids(group_ids)
    else:
        try:
            aggregated = bool(int(aggregated))
        except ValueError:
            return HttpResponseBadRequest("Invalid aggregated parameter value")

        groups = get_groups_by_group_category_ids_aggregated(group_ids, aggregated)

    date_to_groups_mapping = defaultdict(list)

    for group in groups:
        date_to_groups_mapping[group.date_retrieved].append(group)

    for date, groups in date_to_groups_mapping.items():
        group_dicts = []

        for group in groups:
            if group.aggregated:
                group.members_count = 0
            group_dicts.append(group.to_dict())

        group_category_json = {
            "date": date,
            "groups": group_dicts,
        }

        json_response.append(group_category_json)

    return JsonResponse({"Result": json_response})


@api_view(['GET'])
def group_category_count(request, group_category_canvas_id):
    url_parameters_dict = get_url_parameters_dict(request)
    start_date = url_parameters_dict.get(START_DATE_KEY)
    end_date = url_parameters_dict.get(END_DATE_KEY)
    nr_of_dates_limit = url_parameters_dict.get(NR_OF_DATES_LIMIT_KEY)

    if not all([start_date, end_date, nr_of_dates_limit]):
        return HttpResponseBadRequest("Missing required parameters")

    group_categories = get_group_categories_between_dates(group_category_canvas_id, start_date, end_date, nr_of_dates_limit).annotate(
        nr_of_groups_in_category=Count('group')
    )

    json_response = [
        {
            "date": group_category.course.date_retrieved,
            "nr_of_groups_in_category": group_category.nr_of_groups_in_category
        }
        for group_category in group_categories
    ]

    return JsonResponse({"Result": json_response})


def get_groups_by_group_category_ids_aggregated(group_category_ids, aggregated):
    return Group.objects.filter(
        group_category__id__in=group_category_ids,
        aggregated=aggregated
    ).annotate(
        date_retrieved=F('group_category__course__date_retrieved')
    )


def get_groups_by_group_category_ids(group_category_ids):
    return Group.objects.filter(
        group_category__id__in=group_category_ids
    ).annotate(
        date_retrieved=F('group_category__course__date_retrieved')
    )


def get_group_categories_between_dates(group_category_canvas_id, start_date, end_date, nr_of_dates_limit):
    return GroupCategory.objects.filter(
        course__date_retrieved__range=(start_date, end_date),
        canvas_id=group_category_canvas_id,
    ).order_by(
        '-course__date_retrieved'
    )[:nr_of_dates_limit]

