import json

from typing import Dict

import requests
from requests.structures import CaseInsensitiveDict

from statistics_api.definitions import MATOMO_ACCESS_KEY, MATOMO_API_URL

class MatomoApiClient:

    def __init__(self):
        self.web_session = requests.Session()

    def get_single_element_from_url(self, target_url, target_data) -> Dict:
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        web_response = self.web_session.post(target_url, data=target_data, headers=headers)
        if web_response.status_code != 200:
            raise AssertionError(f"Could not retrieve data from Matomo instance at {target_url}")
        return json.loads(web_response.text)

    def get_matomo_visits(self):
        data = f"module=API&method=VisitsSummary.getVisits&idSite=3&period=day&date=yesterday&format=JSON&token_auth={MATOMO_ACCESS_KEY}"
        url = f"{MATOMO_API_URL}"
        return self.get_single_element_from_url(url, data)
    
    def get_matomo_unique_visitors(self):
        data = f"module=API&method=VisitsSummary.getUniqueVisitors&idSite=3&period=day&date=yesterday&format=JSON&token_auth={MATOMO_ACCESS_KEY}"
        url = f"{MATOMO_API_URL}"
        return self.get_single_element_from_url(url, data)

    def get_matomo_page_statistics(self):
        data = f"module=API&method=Actions.getPageUrls&idSite=3&period=day&date=yesterday&expanded=1&filter_limit=-1&format=JSON&token_auth={MATOMO_ACCESS_KEY}"
        url = f"{MATOMO_API_URL}"
        return self.get_single_element_from_url(url, data)

    def get_matomo_visit_frequency(self):
        data = f"module=API&method=VisitFrequency.get&idSite=3&period=day&date=yesterday&format=JSON&token_auth={MATOMO_ACCESS_KEY}"
        url = f"{MATOMO_API_URL}"
        return self.get_single_element_from_url(url, data)