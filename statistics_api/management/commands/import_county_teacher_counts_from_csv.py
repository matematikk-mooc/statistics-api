#!/usr/bin/env python3
import csv
import logging
import sys
from collections import defaultdict
from typing import Tuple, List, Dict

from django.core.management.base import BaseCommand
from django.utils import timezone

from statistics_api.course_info.models import County
from statistics_api.data.county_id_mapping import COUNTY_TO_NEW_COUNTY_ID_MAPPING
from statistics_api.definitions import ROOT_DIR
from statistics_api.utils.utils import parse_year_from_data_file_name, get_county_data_file_paths

class Command(BaseCommand):
    help = "Imports a CSV file with county teacher counts, downloaded from Skoleporten Rapportbygger to the database"

    def handle(self, *args, **options):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.info("Starting importing county teacher counts from CSV file...")
        county_data_file_paths = get_county_data_file_paths(f"{ROOT_DIR}/data")

        for csv_file_path in county_data_file_paths:
            county_ids_and_teacher_counts: List[Tuple[int, int]] = []

            logger.info(f"Opening file {csv_file_path}...")
            with open(csv_file_path, encoding='utf-8') as csvfile:
                row_iterator = csv.reader(csvfile, delimiter="\t")

                row_iterator.__iter__().__next__()  # Moving the iterator to 2nd line

                for row in row_iterator:
                    _, _, county_id, _, _, number_of_teachers = row
                    number_of_teachers = number_of_teachers.replace(" ", "")
                    county_ids_and_teacher_counts.append((int(county_id), int(number_of_teachers)))


            # Creating a dictionary (hashmap) mapping IDs of new counties to their teacher counts
            new_county_id_to_teacher_count_map: Dict[int, int] = defaultdict(int)

            for county_id, teacher_count in county_ids_and_teacher_counts:
                # Mapping old county to new county ID
                # Multiple old counties may belong to a single new county
                new_county_id = COUNTY_TO_NEW_COUNTY_ID_MAPPING[county_id]

                new_county_id_to_teacher_count_map[new_county_id] += teacher_count

            year_of_data = parse_year_from_data_file_name(csv_file_path)
            self.insert_counties(new_county_id_to_teacher_count_map, year_of_data)
            logger.info(f"Finished importing county teacher counts from CSV file.")


    def insert_counties(self, county_id_to_teacher_count_map: Dict[int, int], year_of_data: int):
        for county_id, teacher_count in county_id_to_teacher_count_map.items():
            updated_date = timezone.now()
            obj, created = County.objects.update_or_create(
                county_id=county_id,
                year=year_of_data,
                defaults={
                    'number_of_teachers': teacher_count,
                    'updated_date': updated_date,
                }
            )