import json

import requests

from statistics_api.definitions import CA_FILE_PATH, KPAS_URL


def get_requests(url, path):
    try:
        response = requests.get(url=url + path)
        return response
    except Exception as err:
        print("FetchSchools error while fetching from nsr: {0}".format(err))


def post_to_kpas(path, headers, data=None):
    if data is None:
        data = {}
    web_session = requests.Session()
    if CA_FILE_PATH:
        web_session.verify = CA_FILE_PATH
    try:
        post_response = web_session.post(KPAS_URL + path, data=json.dumps(data), headers=headers)
        print(post_response)
        return post_response
    except Exception as err:
        print("FetchSchools error while posting to kpas: {0}".format(err))