#!/usr/bin/env python3
import csv
import logging
import sys
from typing import Tuple, List

from django.core.management.base import BaseCommand

from statistics_api.clients.db_maintenance_client import DatabaseMaintenanceClient
from statistics_api.definitions import ROOT_DIR

CSV_FILE_PATH_ARG_NAME = "csv_file_path"


class Command(BaseCommand):
    help = "Imports a CSV file with school teacher counts, downloaded from Skoleporten Rapportbygger to the database"

    def add_arguments(self, parser):
        parser.add_argument(CSV_FILE_PATH_ARG_NAME, type=str)

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()

        csv_file_path = f"{ROOT_DIR}{options[CSV_FILE_PATH_ARG_NAME]}"
        organization_numbers_and_teacher_counts: List[Tuple[str, int]] = []

        logger.info(f"Opening file {csv_file_path}...")
        with open(csv_file_path, encoding='utf-8') as csvfile:
            row_iterator = csv.reader(csvfile, delimiter=";")

            row_iterator.__iter__().__next__()  # Moving the iterator to 2nd line

            for row in row_iterator:
                _, organizational_number, _, _, _, _, _, _, _, _, _, _, number_of_teachers, _ = row
                organization_numbers_and_teacher_counts.append((organizational_number, int(number_of_teachers)))

        nr_of_inserts = DatabaseMaintenanceClient.insert_schools(organization_numbers_and_teacher_counts)
        logger.info(f"Inserted {nr_of_inserts} schools from Skoleporten.")
