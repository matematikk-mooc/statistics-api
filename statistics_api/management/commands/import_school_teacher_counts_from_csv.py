#!/usr/bin/env python3
import csv
import logging
import sys
from typing import Tuple, List

from django.core.management.base import BaseCommand

from statistics_api.course_info.models import School
from django.utils import timezone
from datetime import datetime

from django.db import connection

from statistics_api.definitions import ROOT_DIR
from statistics_api.utils.utils import parse_year_from_data_file_name, get_primary_school_data_file_paths

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger()
class Command(BaseCommand):
    help = "Imports a CSV file with school teacher counts, downloaded from Skoleporten Rapportbygger to the database"

    def handle(self, *args, **options):
        logger.info("Starting importing primary school teacher counts from CSV file...")
        primary_school_data_file_paths = get_primary_school_data_file_paths(f"{ROOT_DIR}data/")
        organization_numbers_and_teacher_counts: List[Tuple[str, int]] = []
        for csv_file_path in primary_school_data_file_paths:
            logger.info(f"Opening file {csv_file_path}...")
            with open(csv_file_path, encoding='utf-8') as csvfile:
                row_iterator = csv.reader(csvfile, delimiter="\t")

                row_iterator.__iter__().__next__()  # Moving the iterator to 2nd line

                for row in row_iterator:
                    _, _, _, _, organizational_number, _, _, _, _, number_of_teachers = row
                    number_of_teachers = number_of_teachers.replace(" ", "")
                    organization_numbers_and_teacher_counts.append((organizational_number, int(number_of_teachers)))

        year_of_data = parse_year_from_data_file_name(csv_file_path)
        self.insert_schools(organization_numbers_and_teacher_counts, year_of_data)
        logger.info(f"Finished importing primary school teacher counts from CSV file.")



    def insert_schools(self, organization_numbers_and_teacher_counts: List[Tuple[str, int]], year_of_data: int) -> int:
        # logger.info(len(organization_numbers_and_teacher_counts))
        # for organizational_number, teacher_count in organization_numbers_and_teacher_counts:
        #     obj, created = School.objects.update_or_create(
        #         organization_number=organizational_number,
        #         year=year_of_data,
        #         defaults={
        #             'number_of_teachers': teacher_count,
        #             'updated_date': timezone.now()
        #         }
        #     )
        #     logger.info(f"Added/Updated school with organization number {organizational_number} for year {year_of_data} with teacher count {teacher_count}")
        # logger.info(f"Added/Updated all schools for year {year_of_data} with teacher counts")

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