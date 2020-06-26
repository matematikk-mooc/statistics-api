import json
from typing import Dict

import requests

from statistics_api.definitions import CA_FILE_PATH, KPAS_NSR_API_URL, KPAS_API_URL, KPAS_API_ACCESS_TOKEN


class KpasClient:

    def __init__(self):
        self.web_session = requests.Session()
        self.web_session.headers = {"Authorization": f"Bearer {KPAS_API_ACCESS_TOKEN}"}

        if CA_FILE_PATH:
            self.web_session.verify = CA_FILE_PATH

    def get_schools_by_municipality_id(self, municipality_id: int) -> Dict:
        web_response = self.web_session.get(f"{KPAS_NSR_API_URL}/schools/{municipality_id}")
        return json.loads(web_response.text).get("result")

    def post_trigger_to_activate_schedule_of_job(self) -> None:
        web_response = self.web_session.get(f"{KPAS_API_URL}/run_scheduler")
        return json.loads(web_response.text).get("result")

    def post_enrollment_activity_to_kpas(self, data: Dict) -> requests.Response:
        """
                Ingest enrollment activity date to kpas
                :param data:
                :return:
                """

        web_response = self.web_session.post(f"{KPAS_API_URL}/user_activity", data=data)
        return web_response
