from typing import Tuple

from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory


def compute_total_nr_of_students_for_course_observation(course_observation_id: int) -> int:
    """
    Accepts a course_observation_id (not course Canvas LMS ID, but local DB ID) and returns the total number of students associated
    with this course.
    :param course_id:
    """

    child_group_categories = GroupCategory.objects.filter(course_id=course_observation_id)
    child_groups = []
    for group_category in child_group_categories:
        child_groups += Group.objects.filter(group_category_id=group_category.id)

    total_students = sum([group.members_count for group in child_groups])

    return total_students


def get_n_most_recent_course_observations(course_canvas_id: int, n: int) -> Tuple[CourseObservation]:
    return CourseObservation.objects.filter(canvas_id=course_canvas_id).order_by(
        f"-{CourseObservation.date_retrieved.field.name}")[:n]
