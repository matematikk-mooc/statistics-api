from django.http import JsonResponse

from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory


def group_category(_, group_category_canvas_id: int):
    group_category = GroupCategory.objects.get(canvas_id=group_category_canvas_id)
    groups = Group.objects.filter(group_category=group_category.pk)
    group_dicts = [group.to_dict() for group in groups]
    response = {
        "result": {
            "groups": group_dicts
        }
    }

    return JsonResponse(response)


def group_category_count(_, group_category_canvas_id: int):
    group_category = GroupCategory.objects.get(canvas_id=group_category_canvas_id)
    groups = Group.objects.filter(group_category=group_category.pk)
    response = {
        "result": len(groups)
    }

    return JsonResponse(response)
