import requests
import logging
import time
import json

defaultHeaders = {
    'Accept': '*/*',
    'Accept-Language': 'en-US',
    'User-Agent': 'FordPass/5 CFNetwork/1197 Darwin/20.0.0',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
}

apiHeaders = {
    **defaultHeaders,
    'Application-Id': '1E8C7794-FF5F-49BC-9596-A1E0C86C5B19',    
    'Content-Type': 'application/json',
}

SSO_URI = 'https://sso.ci.ford.com'
API_URI = 'https://usapi.cv.ford.com'
TOKEN_URL = 'https://api.mps.ford.com/api/oauth2/v1'

class Vehicle(object):
    '''Represents a Ford vehicle, with methods for status and issuing commands'''

    def __init__(self, username, password, vin):
        self.username = username
        self.password = password
        self.vin = vin
        self.access_token = None
        self.refresh_token = None
        self.access_expire_time = None
        self.refresh_expire_time = None


    def __auth(self):     
        '''Authenticate and store the token'''

        data = {
            'client_id': '9fb503e0-715b-47e8-adfd-ad4b7770f73b',
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }

        r = requests.post(f'{SSO_URI}/oidc/endpoint/default/token', data=data, headers=defaultHeaders)

        if r.status_code == 200:
            result = r.json()

            self.auth_token = result['access_token']
            logging.info(f'Succesfully fetched auth token and refresh token')            

            data = json.dumps({"code": result['access_token']})

            logging.info('Requesting access token')
            r = self.__makeRequest('PUT', f'{TOKEN_URL}/token', data)

            if r.status_code == 200:

                result = r.json()

                self.access_token = result['access_token']
                self.access_expire_time = time.time() + result['expires_in']
                logging.info(f'Successfully fetched access token (Expires in {result["expires_in"]} seconds)')

                self.refresh_token = result['refresh_token']
                self.refresh_expire_time = time.time() + result['refresh_expires_in']
                logging.info(f'Successfully fetched refresh token (Expires in {result["refresh_expires_in"]} seconds)')
           
            else:
                r.raise_for_status()
        else:
            r.raise_for_status()
    
    def __fetch_refresh_token(self):
        '''
        Fetch a new access token using the refresh token
        '''

        data = json.dumps({"refresh_token": self.refresh_token})

        logging.info('Refreshing access token')
        r = requests.put(f'{TOKEN_URL}/refresh', headers=apiHeaders, data=data)

        if r.status_code == 200:
            result = r.json()
            self.access_token = result['access_token']
            self.access_expire_time = time.time() + result['expires_in']
            logging.info(f'Successfully refreshed access token (Expires in {result["expires_in"]} seconds)')

        else:
            r.raise_for_status()
    
    def __acquireToken(self):
        '''
        Fetch and refresh token as needed
        '''

        if self.access_token == None or self.refresh_expire_time < time.time():
            logging.info('No token, or refresh token has expired, requesting new token')
            self.__auth()

        elif self.access_expire_time < time.time():
            logging.info('Token has expired, refreshing new token')
            self.__fetch_refresh_token()

        else:
            logging.info('Token is valid, continuing')
            logging.info(f'Access token expires in {self.access_expire_time - time.time()} seconds')
            logging.info(f'Refresh token expires in {self.refresh_expire_time - time.time()} seconds')
    
    def status(self):
        '''Get the status of the vehicle'''

        self.__acquireToken() 

        headers = {
            **apiHeaders,
            'auth-token': self.access_token
        }
    
        r = requests.get(f'{API_URI}/api/vehicles/v4/{self.vin}/status', headers=headers)
        
        if r.status_code == 200:
            result = r.json()
            return result['vehiclestatus']
        else:
            r.raise_for_status()
    
    def start(self):
        '''
        Issue a start command to the engine
        '''
        return self.__requestAndPoll('PUT', f'{API_URI}/api/vehicles/v2/{self.vin}/engine/start')

    def stop(self):
        '''
        Issue a stop command to the engine
        '''
        return self.__requestAndPoll('DELETE', f'{API_URI}/api/vehicles/v2/{self.vin}/engine/start')


    def lock(self):
        '''
        Issue a lock command to the doors
        '''
        return self.__requestAndPoll('PUT', f'{API_URI}/api/vehicles/v2/{self.vin}/doors/lock')


    def unlock(self):
        '''
        Issue an unlock command to the doors
        '''
        return self.__requestAndPoll('DELETE', f'{API_URI}/api/vehicles/v2/{self.vin}/doors/lock')

    def __makeRequest(self, method, url, data=None, params=None):
        '''
        Make a request to the given URL, passing data/params as needed
        '''

        headers = {
            **apiHeaders,
            'auth-token': self.access_token,
        }

        return getattr(requests, method.lower())(url, headers=headers, data=data, params=params)

    def __pollStatus(self, url, id):
        '''
        Poll the given URL with the given command ID until the command is completed
        '''
        status = self.__makeRequest('GET', f'{url}/{id}')
        result = status.json()
        if result['status'] == 552:
            logging.info('Command is pending')
            time.sleep(5)
            return self.__pollStatus(url, id) # retry after 5s
        elif result['status'] == 200:
            logging.info('Command completed succesfully')
            return True
        else:
            logging.info('Command failed')
            return False

    def __requestAndPoll(self, method, url):
        self.__acquireToken()
        command = self.__makeRequest(method, url)

        if command.status_code == 200:
            result = command.json()
            return self.__pollStatus(url, result['commandId'])
        else:
            command.raise_for_status()
