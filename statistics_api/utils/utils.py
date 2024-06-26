import re
from datetime import datetime
from os import listdir
from os.path import isfile, join
from typing import Tuple, Dict

from statistics_api.course_info.models import CourseObservation
from statistics_api.course_info.models import Group
from statistics_api.course_info.models import GroupCategory


def parse_year_from_data_file_name(csv_file_name: str) -> int:
    """
    :param csv_file_name: can be, e.g., 'primary_schools_data_2019.csv'.

     For that file name, this function will return the integer '2019'
    """
    print(csv_file_name)
    file_name, extension = csv_file_name.rsplit(".", maxsplit=1)

    year = int(file_name.split("_")[-1])
    return year


def get_closest_matching_year(eligible_years: Tuple[int], target_year: int) -> int:
    return max([year for year in eligible_years if year <= target_year])


def get_target_year(target_date: datetime) -> int:
    # if the course_observation is from a date after 30th of June in any year, then the observation should be matched
    # with teacher counts from that year. If it's from before 30th of June, it should be matched with the year prior.
    # E.g., a course_observation from 12th of May 2019 should be matched with teacher counts from the year 2018-2019,
    # whereas a course_observation from 9th of September 2019 should be matched with teacher counts from year 2019-2020

    if target_date.month >= 7:
        # match with current year
        target_year = target_date.year
    else:
        # match with prior year
        target_year = target_date.year - 1

    return target_year


def get_primary_school_data_file_paths(primary_school_data_dir_path: str) -> Tuple[str]:
    all_file_paths = [join(primary_school_data_dir_path, f) for f in listdir(primary_school_data_dir_path) if isfile(join(primary_school_data_dir_path, f))]
    primary_school_data_file_paths = [f for f in all_file_paths if re.match(r".+\/primary_schools_data_[0-9]{4}\.csv", f)]
    return tuple(primary_school_data_file_paths)


def get_county_data_file_paths(county_data_dir_path: str) -> Tuple[str]:
    all_file_paths = [join(county_data_dir_path, f) for f in listdir(county_data_dir_path) if isfile(join(county_data_dir_path, f))]
    county_data_file_paths = [f for f in all_file_paths if re.match(r".+\/county_data_[0-9]{4}\.csv", f)]
    return tuple(county_data_file_paths)


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
