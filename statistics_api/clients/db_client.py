from datetime import datetime
from typing import List, Dict, Tuple, Union

from django.db import connection

from statistics_api.models.county import County
from statistics_api.models.course_observation import CourseObservation
from statistics_api.models.group import Group
from statistics_api.models.group_category import GroupCategory
from statistics_api.models.school import School


def get_is_school_and_org_nr(group_description: str) -> Tuple[bool, str]:
    _, _, institution_type, _, organization_number = ([s.strip() for s in group_description.split(":")] + [""]*5)[:5]
    return institution_type.strip().lower() == "school", organization_number


class DatabaseClient:

    def insert_courses(self, courses: Tuple[Dict]) -> Tuple[Dict]:
        for course in courses:
            db_course = CourseObservation(canvas_id=course['id'], name=course['name'])
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

    def insert_groups(self, groups: Tuple[Dict]) -> Tuple[Group]:
        db_groups: List[Group] = []

        for group in groups:
            group_is_school, org_nr = get_is_school_and_org_nr(group['description'])
            if not group_is_school:
                org_nr = None
            db_group = Group(canvas_id=group['id'], group_category_id=group['group_category_id'], name=group['name'],
                             description=group['description'], members_count=group['members_count'],
                             organization_number=org_nr, created_at=group['created_at'])
            db_group.save()
            db_groups.append(db_group)
        return tuple(db_groups)

    def insert_schools(self, organization_numbers_and_teacher_counts: List[Tuple[str, int]]) -> int:
        sql_lines = []

        for organizational_number, teacher_count in organization_numbers_and_teacher_counts:
            sql_lines.append(
                f"({organizational_number},{teacher_count},'{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}')")

        sql_statement = f"""INSERT INTO {School._meta.db_table}({School.organization_number.field.name}, 
                                {School.number_of_teachers.field.name}, {School.updated_date.field.name}) VALUES""" \
                        + ", \n".join(sql_lines) + \
                        f"""\n ON DUPLICATE KEY UPDATE
                                {School.number_of_teachers.field.name} = VALUES({School.number_of_teachers.field.name}), 
                                {School.updated_date.field.name} = VALUES({School.updated_date.field.name})"""

        with connection.cursor() as cursor:
            cursor.execute(sql_statement)

        return len(sql_lines)

    def insert_counties(self, county_id_to_teacher_count_map: Dict[int, int]):
        sql_lines = []

        for county_id in county_id_to_teacher_count_map.keys():
            teacher_count = county_id_to_teacher_count_map[county_id]

            sql_lines.append(
                f"({county_id},{teacher_count},'{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}')")

        sql_statement = f"""INSERT INTO {County._meta.db_table}({County.county_id.field.name}, 
                                {County.number_of_teachers.field.name}, {County.updated_date.field.name}) VALUES""" \
                        + ", \n".join(sql_lines) + \
                        f"""\n ON DUPLICATE KEY UPDATE
                                {County.number_of_teachers.field.name} = VALUES({County.number_of_teachers.field.name}), 
                                {County.updated_date.field.name} = VALUES({County.updated_date.field.name})"""

        with connection.cursor() as cursor:
            cursor.execute(sql_statement)