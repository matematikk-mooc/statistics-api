#!/usr/bin/env python3
import csv
import logging
import sys
from datetime import datetime
from typing import Tuple, List

from django.core.management.base import BaseCommand

from statistics_api.definitions import ROOT_DIR
from statistics_api.models.school import School
from django.db import connection

CSV_FILE_PATH_ARG_NAME = "csv_file_path"


class Command(BaseCommand):
    help = "Imports a CSV file downloaded from Skoleporten Rapportbygger to the database"

    def add_arguments(self, parser):
        parser.add_argument(CSV_FILE_PATH_ARG_NAME, type=str)

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()

        csv_file_path = f"{ROOT_DIR}{options[CSV_FILE_PATH_ARG_NAME]}"
        organization_numbers_and_teacher_counts: List[Tuple[int, int]] = []

        logger.debug(f"Opening file {csv_file_path}...")
        with open(csv_file_path, encoding='utf-8') as csvfile:
            row_iterator = csv.reader(csvfile, delimiter=";")

            row_iterator.__iter__().__next__()  # Moving the iterator to 2nd line

            for row in row_iterator:
                _, organizational_number, _, _, _, _, _, _, _, _, _, _, number_of_teachers, _ = row
                organization_numbers_and_teacher_counts.append((int(organizational_number), int(number_of_teachers)))

        # Using raw SQL rather than ORM. Raw SQL is much faster for bulk operations

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

        logger.debug(f"Inserted {len(sql_lines)} schools from NSR.")