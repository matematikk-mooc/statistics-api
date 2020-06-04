from typing import List, Dict, Tuple

from statistics_api.models.course import Course
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory


class DatabaseClient:

    def insert_courses(self, courses: List[Dict]) -> Tuple[Dict]:
        for course in courses:
            db_course = Course(canvas_id=course['id'], name=course['name'],
                               total_nr_of_students=course['total_students'])
            db_course.save()
            course['db_id'] = db_course.pk
        return tuple(courses)

    def insert_group_categories(self, group_categories: List[Dict]) -> Tuple[Dict]:
        for group_category in group_categories:
            db_group_category = GroupCategory(canvas_id=group_category['id'], name=group_category['name'],
                                              course_id=group_category['course_id'])
            db_group_category.save()
            group_category['db_id'] = db_group_category.pk
        return tuple(group_categories)

    def insert_groups(self, groups: Tuple[Dict]) -> None:
        db_groups = [Group(canvas_id=group['id'], group_category_id=group['group_category_id'], name=group['name'],
                           description=group['description'], members_count=group['members_count']) for group in groups]
        Group.objects.bulk_create(db_groups)
