from netmiko import ConnectHandler
import csv
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor
import requests
import time
import logging
from datetime import datetime
import sys
import difflib


class ConnectionParameters:
    def __init__(self, username, password):
        self.ip = None
        self.username = username
        self.password = password
        self.secret = password
        self.device_type = 'cisco_ios'


class CiscoIOSDevice:
    def __init__(self, ip, connection_parameters):
        self.ip = ip
        self.connection_parameters = connection_parameters
        self.connection_parameters.ip = self.ip
        self.hostname = None
        self.registered = False
        self.dlc = False
        self.__session = None

    def connect(self):
        try:
            self.__session = ConnectHandler(**self.connection_parameters.__dict__)
            self.__session.enable()
            if not self.hostname:
                self.hostname = self.__session.find_prompt().replace('#', '')
            logging.info(f'{self.hostname} :: {self.ip} :: Connected :: {datetime.now()}')
            return self.__session
        except: # Add more specific exceptions
            logging.error(f'{self.ip} :: Not able to connect :: {datetime.now()}')

    def disconnect(self):
        self.__session.disconnect()
        logging.info(f'{self.hostname} :: {self.ip} :: Disconnected :: {datetime.now()}')
        self.__session = None

    def configuration_check(self):
        verification_commands = ['show run']
        return [(self.__session.send_command(command)).splitlines() for command in verification_commands]

    def check_status(self):
        show_license = self.__session.send_command('show license status')
        status = []
        for line in show_license.splitlines():
            if 'Status:' in line:
                status.append(line.strip()[7:])
        status.pop(0)
        registration_status = status[0]
        if registration_status == 'REGISTERED':
            self.registered = True
        #dlc_status = status[2]
        #if dlc_status != 'Not started':
            #self.dlc = True
        return self.registered

    def register(self, token):
        pre_check = self.configuration_check()
        self.__session.send_config_from_file(config_file='smart_license_config.txt')
        logging.info(f'{self.hostname} :: {self.ip} :: Configuration for Smart License is done :: {datetime.now()}')
        post_check = self.configuration_check()
        with open(f'{self.hostname}.html', 'w') as diff_file:
            diff = difflib.HtmlDiff()
            diff_file.write(diff.make_file(pre_check, post_check, fromdesc=f'{self.hostname} :: {datetime.now()}', todesc=f'{self.hostname} :: {datetime.now()}'))
        self.__session.save_config()
        logging.info(f'{self.hostname} :: {self.ip} :: Configuration is saved :: {datetime.now()}')
        self.__session.send_command(f'license smart register idtoken {token}')
        logging.info(f'{self.hostname} :: {self.ip} :: Smart License registration has started :: {datetime.now()}')

    def wait_for_registration(self, seconds):
        for i in range(int(seconds) + 1):
            time.sleep(1)
            if i % 10 == 0:
                self.check_status()
                if self.registered:
                    logging.info(
                        f'{self.hostname} :: {self.ip} :: Devices has been registered :: {datetime.now()}')
                    break
        if not self.registered:
            self.__session.send_command('show license status')
            # get error
            # registration_error =
            logging.warning(
                f'{self.hostname} :: {self.ip} :: {registration_error} :: {datetime.now()}')

    def run_dlc(self):
        self.__session.send_command('run dlc')
        logging.info(f'{self.hostname} :: {self.ip} :: DLC started :: {datetime.now()}')


class SmartLicenseOnPrem:
    def __init__(self, slop_username, slop_password):
        self.username = slop_username
        self.password = slop_password
        self.grant_type = 'client_credentials'
        self.client_id = ''
        self.client_secret = ''
        self.url = ''
        self.virtual_account = ''

    def get_auth_token(self):
        auth_url = self.url + '/oauth/token'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        auth_data = f'''
            {{"grant_type": f"{self.grant_type}", 
            "username": f"{self.username}",
            "password": f"{self.password}",
            "client_id": f"{self.client_id}",
            "client_secret": f"{self.client_secret}"}}
            '''
        token = requests.post(auth_url, headers=headers, data=auth_data, verify=False)
        auth_token = token.json()['access_token']
        return auth_token

    def get_token(self, auth_token):
        token_url = self.url + '/api/v1/accounts/{self.virtual_account}/virtual-accounts/Default/tokens'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': f'Bearer {auth_token}'}
        response = requests.get(token_url, headers=headers, verify=False)
        return response.json()['tokens'][0]['token']


if __name__ == '__main__':

    logging.basicConfig(filename='smart_license.log',
                        format = '%(threadName)s: %(levelname)s: %(message)s',
                        level=logging.DEBUG)

    def smart_license_registration(device):
        device.connect()
        if not device.registered:
            device.register(token='123')
            device.wait_for_registration(seconds=300)
            if device.registered:
                device.run_dlc()
            device.disconnect()


    username = input('Enter user login: ')
    password = getpass('Enter user password: ')

    devices = [CiscoIOSDevice('10.0.0.61', ConnectionParameters(username, password)),
               CiscoIOSDevice('10.0.0.62', ConnectionParameters(username, password))]

    #with open('inventory.csv') as inventory_file:
        #reader = csv.DictReader(inventory_file)
        #for device in reader:
            #devices.append(CiscoIOSDevice(device['IP Address'], connection_parameters))

    #slop_username = input('Enter SmartLicenseOnPrem user: ')
    #slop_password = getpass('Enter SmartLicenseOnPrem password: ')

    #slop = SmartLicenseOnPrem(slop_username, slop_password)
    #auth_token = slop.get_auth_token()
    #token = slop.get_token(auth_token)

    with ThreadPoolExecutor(max_workers=10) as executor:
        result = executor.map(smart_license_registration, devices)
        for device in result:
            print(device)

