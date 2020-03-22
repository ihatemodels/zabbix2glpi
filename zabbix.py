import json
import requests

class ZabbixError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'\nZabbix Error: {self.message}'

class Zabbix(object):

    def __init__(self, user=None, password=None, url=None):

        if user is None or password is None or url is None:
            raise ZabbixError('Missing log-in parameteres')

        self.url = f'{url}/zabbix/api_jsonrpc.php'
        self.headers = {"Content-Type": "application/json-rpc"}

        self.user = user
        self.password = password
        self.token = None
        self.__set_token()
        
    def __repr__(self):
        return f'Zabbix token: {self.token}'

    def __set_token(self):

        body = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {"user": self.user, "password": self.password},
            "id": 1,
            "auth": None,
        }

        body = json.dumps(body)

        response = requests.post(self.url, headers=self.headers, data=body)
     
        if 'result' in response.json():
            self.token = response.json()['result']
        else:
            raise ZabbixError(response.json()['error']['data'])

    def ack_event(self, glpi_ticket=None, event_id=None):

        if event_id is None:
            raise ZabbixError('Missing parameter event_id')
        
        if glpi_ticket:
            message = f'Glpi Ticket: {glpi_ticket} Created'
        else:
            message = 'Glpi Ticket Created'

        body = {
            "jsonrpc": "2.0",
            "method": "event.acknowledge",
            "params": {
                "eventids": event_id,
                "action": 6,
                "message": message,
            },
            "auth": self.token,
            "id": 1
        }


        body = json.dumps(body)

        response = requests.post(self.url, headers=self.headers, data=body)

        if 'error' in response.json():
            raise ZabbixError(response.json()['error']['data'])
