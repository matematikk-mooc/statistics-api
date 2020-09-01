#!/usr/bin/env python3
import csv
import logging
import sys
from collections import defaultdict
from typing import Tuple, List, Dict

from django.core.management.base import BaseCommand

from statistics_api.clients.db_maintenance_client import DatabaseMaintenanceClient
from statistics_api.data.county_id_mapping import COUNTY_TO_NEW_COUNTY_ID_MAPPING
from statistics_api.definitions import ROOT_DIR
from statistics_api.utils.utils import parse_year_from_data_file_name

CSV_FILE_PATH_ARG_NAME = "csv_file_path"


class Command(BaseCommand):
    help = "Imports a CSV file with county teacher counts, downloaded from Skoleporten Rapportbygger to the database"

    def add_arguments(self, parser):
        parser.add_argument(CSV_FILE_PATH_ARG_NAME, type=str)

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()

        csv_file_name = options[CSV_FILE_PATH_ARG_NAME]
        csv_file_path = f"{ROOT_DIR}{csv_file_name}"
        county_ids_and_teacher_counts: List[Tuple[int, int]] = []

        logger.info(f"Opening file {csv_file_path}...")
        with open(csv_file_path, encoding='utf-8') as csvfile:
            row_iterator = csv.reader(csvfile, delimiter=";")

            row_iterator.__iter__().__next__()  # Moving the iterator to 2nd line

            for row in row_iterator:
                _, county_id, _, _, _, _, _, _, _, _, _, _, number_of_teachers, _ = row
                county_ids_and_teacher_counts.append((int(county_id), int(number_of_teachers)))


        # Creating a dictionary (hashmap) mapping IDs of new counties to their teacher counts
        new_county_id_to_teacher_count_map: Dict[int, int] = defaultdict(int)

        for county_id, teacher_count in county_ids_and_teacher_counts:
            # Mapping old county to new county ID
            # Multiple old counties may belong to a single new county
            new_county_id = COUNTY_TO_NEW_COUNTY_ID_MAPPING[county_id]

            new_county_id_to_teacher_count_map[new_county_id] += teacher_count

        year_of_data = parse_year_from_data_file_name(csv_file_name)
        DatabaseMaintenanceClient.insert_counties(new_county_id_to_teacher_count_map, year_of_data)
        logger.info(f"Inserted {len(county_ids_and_teacher_counts)} counties from Skoleporten.")