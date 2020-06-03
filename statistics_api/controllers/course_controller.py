from django.http import JsonResponse

from statistics_api.models.course import Course
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory


def course(_, course_canvas_id: int):
    course = Course.objects.get(canvas_id=course_canvas_id)
    child_group_categories = GroupCategory.objects.filter(course_id=course.id)
    child_groups = []
    for group_category in child_group_categories:
        child_groups += Group.objects.filter(group_category_id=group_category.id)

    total_students = sum([group.members_count for group in child_groups])

    group_category_names = [group_category.name for group_category in child_group_categories]
    group_category_member_counts = []
    for group_category in child_group_categories:
        group_category_member_counts.append(len([group for group in child_groups if group.group_category_id == group_category.id]))

    groups_dict = dict(zip(group_category_names, group_category_member_counts))

    response = {
        "result": {
            "antallBrukere": total_students,
            "groups": groups_dict
        }
    }

    return JsonResponse(response)


def course_count(_, course_canvas_id: int):
    course = Course.objects.get(canvas_id=course_canvas_id)
    child_group_categories = GroupCategory.objects.filter(course_id=course.id)
    child_groups = []
    for group_category in child_group_categories:
        child_groups += Group.objects.filter(group_category_id=group_category.id)

    total_students = sum([group.members_count for group in child_groups])

    response = {
        "result": {
            "antallBrukere": total_students
        }
    }

    return JsonResponse(response)
