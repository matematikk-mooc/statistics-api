#!/usr/bin/python3
import json
import os
from datetime import datetime

import requests


def get_age_of_data_on_statistics_api(base_url: str, municipality_id, course_id) -> int:
    """
    :param course_id: Canvas course ID for which to retrieve data
    :param municipality_id: Municipality ID for which to retrieve data
    :param base_url: Base URL of statistics-api service
    """

    url = f"{base_url}/api/statistics/primary_schools/municipality/{municipality_id}/course/{course_id}"
    response = requests.get(url)
    json_result = json.loads(response.text)

    timestamp_str = json_result["Result"][0]["date"]
    date_part, time_part = timestamp_str.split("T")
    year, month, day = [int(i) for i in date_part.split("-")]
    hour, minute = [int(i) for i in time_part.split(":")[:2]]
    seconds = int(time_part.split(":")[-1].split(".")[0])
    date_obj = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=seconds)
    time_diff = datetime.now() - date_obj
    return int(time_diff.total_seconds())


if __name__ == '__main__':
    url = os.getenv('API_BASE_URL')
    municipality_id = os.getenv('MUNICIPALITY_ID')
    course_id = os.getenv('COURSE_ID')
    data_max_age = int(os.getenv('DATA_MAX_AGE'))

    age_of_data_in_seconds = get_age_of_data_on_statistics_api(url, municipality_id, course_id)
    if age_of_data_in_seconds > data_max_age:
        exit(1)
    else:
        exit(0)
