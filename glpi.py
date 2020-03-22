import requests
import base64

class TicketCreationError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'\nTicketCreationError: {self.message}'

class UserMissingError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'\nUser: {self.message} not found in glpi_users:'

class TicketAssignError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'\nTicketAssignError: {self.message}'

class TicketMissingError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'\nTicketID: {self.message} Not Found'

class ClossingConnectionError(Exception):

    def __str__(self):
        return 'Session not established'

class Glpi(object):
    """
    GLPI Class 

    Parameters:
            user (str): GLPI username
            password (str): Password for the user
            app_token(str): User generated app token
            url(str): GLPI url: <http://my.glpy.domain>

    Attributes:
            last.created_ticket_id(int)
            glpi_users(dict) 
    """

    def __init__(self, user=None, password=None, app_token=None, url=None):
        
        if user is None or password is None or app_token is None:
            raise Exception('Missing log-in parameteres')

        self.user = user
        self.password = password 
        self.app_token = app_token 
        self.url = url

        self.url_web = self.url + '/glpi/plugins/webservices/rest.php?'

        self.session = None
        self.glpi_users = {}
        self.last_created_ticket_id = int

        self.__set_session()
        self.__set_glpi_users()

        self.headers = {
            'Content-Type': 'application/json',
            'Session-Token': self.session,
            'App-Token': self.app_token,
        }
    def kill_session(self):

        kill_url = self.url + '/glpi/apirest.php/killSession'
        try:
            requests.get(kill_url, headers=self.headers)
        except AttributeError:
            raise ClossingConnectionError()

    def __repr__(self):

        return (
            f'GLPI Users(username:userid): {self.glpi_users}\n'
            f'Username: {self.user}\n'
            f'Session_token: {self.session}\n'
            f'Url: {self.url}\n'
            f'WebServices Url: {self.url_web}'
        )

    def __set_session(self):

        credentials = 'Basic ' + base64.b64encode(str.encode(self.user + ':' + self.password)).decode("utf-8")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': credentials,
            'App-Token': self.app_token,
        }

        init_url = self.url + '/glpi/apirest.php/initSession'

        try:
            response = requests.get(init_url, headers=headers, timeout=5)
        except:
            raise Exception("Connection error to GLPI server")

        try:
            result = response.json()['session_token']
            self.session = str(result)
        except:
            raise ConnectionError("Can't connect to glpi server")

    def __set_glpi_users(self):
        """
        Set glpi_users (dict)
        username:user_id"""

        headers = {
            'Content-Type': 'application/json',
            'session': self.session,
            'method':'glpi.listUsers',
        }

        users = requests.post(self.url_web, params=headers)
 
        for item in users.json():
            self.glpi_users.update({item['name'] : item['id']})

    def get_users(self):
        """
        Returns:
            Dictionary {username:userid}
        """
        return self.glpi_users

    def create_ticket(self, hostname, eventid, triggerid, ticketname, urgency):

        content = f'Host: {hostname} TriggerID: {triggerid}, EventID: {eventid}'

        headers = {
            'Content-Type': 'application/json',
            'session': self.session,
            'method':'glpi.createTicket',
            'title': ticketname,
            'urgency':urgency,
            'content': content
        }

        response = requests.post(self.url_web, params=headers)
        resp_json = response.json()

        if 'faultCode' in resp_json:
            raise TicketCreationError(resp_json['faultString'])

        self.last_created_ticket_id = resp_json['id']

        print(f"Ticket with id {resp_json['id']} created")
        
    def assign_ticket(self, user, ticketid):
        """
        Assign existing GLPI ticket to
        specific user  
        
        Args:
            user(str): login-username in GLPI
            ticketid(int): uniqe ticket id 

            self.last_created_ticket_id can be
            used to obtain the last created ticket.

        Raises:
            UserMissingError: Raised when no 
            user is provided
        """
        if not user in self.glpi_users.keys():
            raise UserMissingError(user)

        headers = {
            'Content-Type': 'application/json',
            'session': self.session,
            'method':'glpi.setTicketAssign',
            'ticket':ticketid,
            'user':self.glpi_users[user],
        }

        response = requests.post(self.url_web, params=headers)

        json_obj = response.json()

        if 'faultString' in json_obj.keys():
            raise TicketAssignError(json_obj['faultString'])

    def close_ticket(self, ticket_id):


        url = f'{self.url}/glpi/apirest.php/Ticket/{ticket_id}'

        payload = '{"input" : {"status" : "6" }}'

        response = requests.put(url=url, headers=self.headers, data=payload)

        if None in response.json():
            raise TicketMissingError(ticket_id)
