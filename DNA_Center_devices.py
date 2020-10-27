import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import time
import csv


class Device:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)
        self.dnac_url = ''
        self.__token = None
        self.__site_id = None

    def get_token(self):
        url = self.dnac_url + '/dna/system/api/v1/auth/token'
        headers = {'Content-Type': 'application/json'}
        self.__token = requests.post(url, headers=headers, auth=HTTPBasicAuth('admin', 'password'), verify=False).json()['Token']

    def get_site_id(self):
        url = self.dnac_url + f'/dna/intent/api/v1/site?type=building'
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.__token}
        buildings = requests.get(url, headers=headers, verify=False).json()['response']
        for building in buildings:
            if building['name'] == self.site_name:
                self.__site_id = building['id']

    def add_device(self):
        url = self.dnac_url + '/dna/intent/api/v1/network-device'
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.__token}
        data = {"cliTransport": "ssh",
                "enablePassword": "password",
                "ipAddress": [self.ip_address],
                "password": "password",
                "snmpROCommunity": "public",
                "snmpRWCommunity": "private",
                "snmpRetry": 3,
                "snmpTimeout": 5,
                "snmpVersion": "v2",
                "type": "NETWORK_DEVICE",
                "userName": "admin"}
        return requests.post(url, headers=headers, json=data, verify=False).json()['response']['taskId']

    def add_device_status(self, task_id):
        url = self.dnac_url + f'/dna/intent/api/v1/task/{task_id}'
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.__token}
        pprint(requests.get(url, headers=headers, verify=False).json()['response'])

    def assign_device(self):
        url = self.dnac_url + f'/dna/system/api/v1/site/{self.__site_id}/device'
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.__token, '__runsync': 'true'}
        data = {"device":[{"ip": self.ip_address}]}
        pprint(requests.post(url, headers=headers, json=data, verify=False).json())

if __name__ == '__main__':


    with open('devices_and_sites.csv') as data_file:
        reader = csv.DictReader(data_file)
        for row in reader:
            device = Device(row)

            device.get_token()
            device.get_site_id()

            task_id = device.add_device()
            time.sleep(20)
            device.add_device_status(task_id)

            device.assign_device()
