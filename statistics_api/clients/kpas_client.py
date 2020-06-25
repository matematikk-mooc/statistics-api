import json
from typing import Dict

import requests

from statistics_api.definitions import CA_FILE_PATH, KPAS_API_URL


class KpasClient:

    def __init__(self):
        self.web_session = requests.Session()
        self.web_session.verify = CA_FILE_PATH if CA_FILE_PATH else self.web_session.verify

    def get_schools_by_municipality_id(self, municipality_id: int) -> Dict:
        web_response = self.web_session.get(f"{KPAS_API_URL}/schools/{municipality_id}")
        return json.loads(web_response.text).get("result")
