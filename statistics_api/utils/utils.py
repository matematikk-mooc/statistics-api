from typing import Tuple, List, Dict

from statistics_api.definitions import CATEGORY_CODES, PERCENTAGE_INTERVALS
from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory


def calculate_enrollment_percentage_category(enrollment_count: int, teacher_count: int) -> int:
    percentage_enrollment = enrollment_count / teacher_count if teacher_count > 0 else 0

    for category_code in CATEGORY_CODES:
        lower_bound = (PERCENTAGE_INTERVALS[category_code]) / 100
        if percentage_enrollment <= lower_bound:
            return category_code

    return CATEGORY_CODES[-1]


def filter_high_schools(schools: Tuple[Dict]) -> Tuple[Dict]:
    return tuple([school for school in schools if school['ErVideregaaendeSkole'] == True])


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