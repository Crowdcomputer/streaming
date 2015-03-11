import json

import requests


class Flower:
    DEFAULT_API_URL = 'https://api.crowdflower.com/v1/'
    DEFAULT_API_HEADERS = {'content-type': 'application/json'}

    def __init__(self, api_key, api_url=DEFAULT_API_URL, api_headers=DEFAULT_API_HEADERS):
        self.api_key = api_key
        self.api_url = api_url
        self.api_headers = api_headers

    def _getRequestUrl(self, type, id):
        extention = ''
        if type == 'job':
            extention = 'jobs/' + str(id) + '.json'
        if type == 'units':
            extention = 'jobs/' + str(id) + '/units.json'
        return self.api_url + extention + "?key=" + self.api_key

    def updateJob(self, job_id, attrs):
        request_url = self._getRequestUrl('job', job_id)
        data = {
            'job': attrs
        }
        return requests.put(request_url, data=json.dumps(data), headers=self.api_headers)

    def uploadUnit(self, job_id, data):
        request_url = self._getRequestUrl('units', job_id)
        data = {
            'unit': {
                'data': data
            }
        }
        return requests.post(request_url, data=json.dumps(data), headers=self.api_headers)

    @staticmethod
    def parseWebhook(response_data):
        if response_data['signal'] == 'unit_complete':
            # data = response_data['payload']
            payload = response_data['payload']
            d_dict = json.loads(payload[0])
            res = d_dict['results']
            jud = res['judgments']
            return jud
        return False