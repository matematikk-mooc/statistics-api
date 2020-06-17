import json

import requests

from statistics_api.definitions import CANVAS_ACCESS_KEY, CA_FILE_PATH
from statistics_api.settings import KPAS_URL


def get_requests(url, path):
    try:
        response = requests.get(url=url + path)
        return response
    except Exception as err:
        print("FetchSchools error while fetching from nsr: {0}".format(err))


def post_to_kpas(path, data, headers):
    web_session = requests.Session()
    web_session.verify = CA_FILE_PATH
    try:
        post_response = web_session.post(KPAS_URL + path, data=json.dumps(data), headers=headers)
        print(post_response)
        return post_response
    except Exception as err:
        print("FetchSchools error while posting to kpas: {0}".format(err))


class FetchSchools:
    def __init__(self):
        self.nsr_url = "https://data-nsr.udir.no"
        self.headers = {"Accept": "application/json"}

    def fetch_fylkes(self):
        """
        curl -X GET --header 'Accept: application/json'
        'https://data-nsr.udir.no/fylker'

        :return:
        """
        path = "/fylker"
        counties = get_requests(url=self.nsr_url, path=path)
        for countie in counties.json():
            path = "/counties"
            headers = {"Content-Type": "application/json", }
            post_to_kpas(path=path, headers=headers, data=countie)

    def fetch_kommunes(self):
        """
        curl -X GET --header 'Accept: application/json'
        'https://data-nsr.udir.no/kommune'

        :return:
        """
        path = "/kommuner"
        communities = get_requests(url=self.nsr_url, path=path)
        data = {}
        for kommune in communities.json():
            data['Fylkesnr'] = kommune['Fylkesnr']
            data['Navn'] = kommune['Navn']
            data['OrgNr'] = kommune['OrgNr']
            data['Kommunenr'] = kommune['Kommunenr']

            path = "/communities"
            headers = {"Content-Type": "application/json", }
            post_to_kpas(path=path, headers=headers, data=data)

    def fetch_skoles(self):
        """
        fetches all enheter and filters only skole related fileds
        curl -X GET --header 'Accept: application/json'
        'https://data-nsr.udir.no/enheter'

        :return:
        """
        path = "/enheter"
        enheter = get_requests(url=self.nsr_url, path=path)
        data = {}
        for enhet in enheter.json():
            data['NSRId'] = enhet['NSRId']
            data['Navn'] = enhet['Navn']
            data['OrgNr'] = enhet['OrgNr']
            data['Kommunenr'] = enhet['KommuneNr']
            data['ErSkole'] = enhet['ErSkole']
            data['ErSkoleEier'] = enhet['ErSkoleEier']
            data['ErGrunnSkole'] = enhet['ErGrunnSkole']
            data['ErPrivatSkole'] = enhet['ErPrivatSkole']
            data['ErOffentligSkole'] = enhet['ErOffentligSkole']
            data['ErVideregaaendeSkole'] = enhet['ErVideregaaendeSkole']
            if enhet['ErSkole'] or enhet['ErSkoleEier'] or enhet['ErGrunnSkole'] or enhet['ErPrivatSkole'] or enhet['ErOffentligSkole'] or enhet['ErVideregaaendeSkole']:
                path = "/schools"
                headers = {"Content-Type": "application/json", }
                post_to_kpas(path=path, headers=headers, data=data)
