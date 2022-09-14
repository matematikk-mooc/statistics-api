import json
from typing import Dict, Tuple, Union

import requests

from statistics_api.definitions import CA_FILE_PATH, KPAS_NSR_API_URL, KPAS_API_URL, KPAS_API_ACCESS_TOKEN


class KpasClient:

    def __init__(self):
        self.web_session = requests.Session()
        self.web_session.headers = {"Authorization": f"Bearer {KPAS_API_ACCESS_TOKEN}"}

        if CA_FILE_PATH:
            self.web_session.verify = CA_FILE_PATH

    def get_schools_by_municipality_id(self, municipality_id: int) -> Tuple[Dict]:
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/communities/{municipality_id}/schools/")
        response_json = web_response.json()
        if response_json.get("result") is None:
            return None
        return tuple(response_json.get("result"))

    def get_schools_by_county_id(self, county_id: int) -> Tuple[Dict]:
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/counties/{county_id}/schools/")
        response_json = web_response.json()
        if response_json.get("result") is None:
            return None
        return tuple(response_json.get("result"))

    def get_municipalities_by_county_id(self, county_id):
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/counties/{county_id}/communities/")
        response_json = web_response.json()
        if response_json.get("result") is None:
            return None
        return tuple(response_json.get("result"))

    def post_trigger_to_activate_schedule_of_job(self) -> None:
        web_response = self.web_session.post(f"{KPAS_API_URL}/run_scheduler")
        assert web_response.status_code == 200

    def get_county(self, county_id: int) -> Union[Dict, None]:
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/counties/{county_id}")
        response_json = web_response.json()
        if response_json.get("result") is None:
            return None
        return response_json.get("result")

    def get_municipality(self, municipality_id: int) -> Union[Dict, None]:
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/communities/{municipality_id}")
        response_json = web_response.json()
        if response_json.get("result") is None:
            return None
        return response_json.get("result")

    def get_all_high_schools(self) -> Tuple[Dict]:
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/schools", params={"only_high_schools": True})
        response_json = web_response.json()
        if response_json.get("result") is None:
            return None
        return tuple(response_json.get("result"))
