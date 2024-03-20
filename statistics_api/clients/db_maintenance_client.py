from datetime import datetime
from typing import Tuple, Dict, List

from django.db import connection

from statistics_api.course_info.models import County
from statistics_api.course_info.models import CourseObservation
from statistics_api.course_info.models import Group
from statistics_api.course_info.models import GroupCategory
from statistics_api.course_info.models import School
from statistics_api.course_info.utils import Utils

import logging

logger = logging.getLogger(__name__)

class DatabaseMaintenanceClient:

    @staticmethod
    def update_group_org_nrs(group_ids_and_org_nrs_for_update: Tuple[Tuple[int, str]]) -> None:
        # NB! MAX_ALLOWED_PACKET on MySQL server needs to be higher than default for this line to work.
        # Django ORM is not used here because bulk updates are far too slow, even with bulk_update method
        update_group_organization_numbers_query: str = DatabaseMaintenanceClient.get_update_group_organization_numbers_query(
            group_ids_and_org_nrs_for_update)

        with connection.cursor() as cursor:
            cursor.execute(update_group_organization_numbers_query)
            cursor.close()

    @staticmethod
    def insert_courses(courses: Tuple[Dict]) -> Tuple[Dict]:
        for course in courses:
            db_course = CourseObservation(canvas_id=course['id'], name=course['name'].strip())
            db_course.save()
            course['db_id'] = db_course.pk
        return tuple(courses)

    @staticmethod
    def insert_group_categories(group_categories: List[Dict]) -> Tuple[Dict]:
        for group_category in group_categories:
            db_group_category = GroupCategory(
                canvas_id=group_category['id'],
                name=group_category['name'].strip(),
                course_id=group_category['course_id']
            )
            db_group_category.save()
            group_category['db_id'] = db_group_category.pk
        return tuple(group_categories)

    @staticmethod
    def insert_groups(groups: Tuple[Dict]) -> Tuple[Group]:
        db_groups: List[Group] = []

        for group in groups:
            if group.get("description"):
                group_is_school, org_nr = Utils.get_is_school_and_org_nr(group['description'])
            else:
                group_is_school = False
            if not group_is_school:
                org_nr = None
            is_aggregated = False
            if group['members_count'] < 5:
                is_aggregated = True
            db_group = Group(
                canvas_id=group['id'],
                group_category_id=group['group_category_id'],
                name=group['name'].strip(),
                description=group['description'],
                members_count=group['members_count'],
                organization_number=org_nr,
                created_at=group['created_at'],
                aggregated=is_aggregated
            )
            db_group.save()
            db_groups.append(db_group)
        return tuple(db_groups)

    @staticmethod
    def insert_schools(organization_numbers_and_teacher_counts: List[Tuple[str, int]], year_of_data: int) -> int:
        sql_lines = []

        for organizational_number, teacher_count in organization_numbers_and_teacher_counts:
            sql_lines.append(
                f"({organizational_number},{teacher_count},'{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}',{year_of_data})")

        sql_statement = f"""INSERT INTO {School._meta.db_table}({School.organization_number.field.name},
            {School.number_of_teachers.field.name}, {School.updated_date.field.name}, {School.year.field.name}) VALUES""" \
            + ", \n".join(sql_lines) + \
            f"""\n ON DUPLICATE KEY UPDATE
                {School.number_of_teachers.field.name} = VALUES({School.number_of_teachers.field.name}),
                {School.updated_date.field.name} = VALUES({School.updated_date.field.name})"""

        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            cursor.close()

        return len(sql_lines)

    @staticmethod
    def insert_counties(county_id_to_teacher_count_map: Dict[int, int], year_of_data: int):
        sql_lines = []

        for county_id in county_id_to_teacher_count_map.keys():
            teacher_count = county_id_to_teacher_count_map[county_id]

            sql_lines.append(
                f"({county_id},{teacher_count},'{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}', {year_of_data})")

        sql_statement = f"""INSERT INTO {County._meta.db_table}({County.county_id.field.name},
            {County.number_of_teachers.field.name}, {County.updated_date.field.name}, {County.year.field.name}) VALUES""" \
            + ", \n".join(sql_lines) + \
            f"""\n ON DUPLICATE KEY UPDATE
                {County.number_of_teachers.field.name} = VALUES({County.number_of_teachers.field.name}),
                {County.updated_date.field.name} = VALUES({County.updated_date.field.name})"""

        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            cursor.close()

    def insert_counties2(county_id_to_teacher_count_map: Dict[int, int], year_of_data: int):
        counties_to_insert_or_update = []

        for county_id, teacher_count in county_id_to_teacher_count_map.items():
            county = County(
                county_id=county_id,
                number_of_teachers=teacher_count,
                updated_date=datetime.now(),
                year=year_of_data
            )
            counties_to_insert_or_update.append(county)
        try:
            County.objects.aupdate_or_create(
                counties_to_insert_or_update,
                fields=['number_of_teachers', 'updated_date'],
                update_fields=['number_of_teachers', 'updated_date']
            )
        except Exception as e:
            logger(e)

    def get_update_group_organization_numbers_query(group_ids_and_org_nrs: Tuple[Tuple[int, str]]) -> str:
        sql_values = []

        for group_id, group_org_nr in group_ids_and_org_nrs:
            sql_values.append(
                f"({group_id}, {0}, '', NULL, {0}, {0}, {0}, {1}, '{group_org_nr}')")

        return f"""INSERT INTO `group` VALUES\n""" \
            + ", \n".join(sql_values) + \
            f"""\nON DUPLICATE KEY UPDATE organization_number = VALUES(organization_number)"""
