import requests
import logging
import time

defaultHeaders = {
    'Accept': '*/*',
    'Accept-Language': 'en-us',
    'User-Agent': 'fordpass-na/353 CFNetwork/1121.2.2 Darwin/19.3.0',
    'Accept-Encoding': 'gzip, deflate, br',
}

apiHeaders = {
    **defaultHeaders,
    'Application-Id': '71A3AD0A-CF46-4CCF-B473-FC7FE5BC4592',    
    'Content-Type': 'application/json',
}

baseUrl = 'https://usapi.cv.ford.com/api'
mpsUrl = "https://api.mps.ford.com/api"

class Vehicle(object):
    '''Represents a Ford vehicle, with methods for status and issuing commands'''

    def __init__(self, username, password, vin):
        self.username = username
        self.password = password
        self.vin = vin
        self.token = None
        self.expires = None
    
    def auth(self):       
        '''Authenticate and store the token'''

        data = {
            'client_id': '9fb503e0-715b-47e8-adfd-ad4b7770f73b',
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }

        headers = {
            **defaultHeaders,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.post('https://fcis.ice.ibmcloud.com/v1.0/endpoint/default/token', data=data, headers=headers)        

        if r.status_code == 200:
            logging.info('Succesfully fetched token')
            result = r.json()
            self.token = result['access_token']
            self.expiresAt = time.time() + result['expires_in']
            return True
        else:
            r.raise_for_status()
    
    def __acquireToken(self):
        '''Fetch and refresh token as needed'''

        if (self.token == None) or (time.time() >= self.expiresAt):
            logging.info('No token, or has expired, requesting new token')
            self.auth()
        else:
            logging.info('Token is valid, continuing')
            pass
    
    def status(self):
        '''Get the status of the vehicle'''

        self.__acquireToken() 

        params = {
            'lrdt': '01-01-1970 00:00:00'
        }

        headers = {
            **apiHeaders,
            'auth-token': self.token
        }

        r = requests.get(f'{baseUrl}/vehicles/v4/{self.vin}/status', params=params, headers=headers)
        
        if r.status_code == 200:
            result = r.json()
            return result['vehiclestatus']
        else:
            r.raise_for_status()
    
    def plugstatus(self):
        """Get the plug status of a FordPass EV"""

        self.__acquireToken()

        headers = {**apiHeaders, "auth-token": self.token, "vin": self.vin}

        r = requests.get(f'{mpsUrl}/vpoi/chargestations/v3/plugstatus', headers=headers)

        if r.status_code == 200:
            result = r.json()
            return result
        else:
            r.raise_for_status()

    def journeys(self, start, end):
        """Get the journeys of a FordPass vehicle for a given period"""

        self.__acquireToken()

        headers = {**apiHeaders, "auth-token": self.token}

        r = requests.get(f'{mpsUrl}/journey-info/v1/journeys?countryCode=USA&vins={self.vin}&startDate={start}&endDate={end}&clientVersion=iOS3.29.0', headers=headers)

        if r.status_code == 200:
            result = r.json()
            return result
        else:
            r.raise_for_status()

    def journey_details(self, id):
        """Get the journey details of a FordPass journey"""

        self.__acquireToken()

        headers = {**apiHeaders, "country-code": "USA", "auth-token": self.token}

        r = requests.get(
            f'{mpsUrl}/journey-info/v1/journey/details/{id}?vin={self.vin}&clientVersion=iOS3.29.0',
            headers=headers
        )

        if r.status_code == 200:
            result = r.json()
            return result
        else:
            r.raise_for_status()

    def chargelogs(self):
        """Get the charge logs of a FordPass EV"""

        self.__acquireToken()

        headers = {**apiHeaders, "auth-token": self.token}
        vin = {'vin': self.vin}
        r = requests.post(f'{mpsUrl}/cevs/v2/chargelogs/retrieve', headers=headers, json=vin)

        if r.status_code == 200:
            result = r.json()
            return result
        else:
            r.raise_for_status()

    def triplogs(self):
        """Get the trip logs of a FordPass vehicle"""

        self.__acquireToken()

        headers = {**apiHeaders, "auth-token": self.token}
        vin = {'vin': self.vin}
        r = requests.post(f'{mpsUrl}/cevs/v1/triplogs/retrieve', headers=headers, json=vin)

        if r.status_code == 200:
            result = r.json()
            return result
        else:
            r.raise_for_status()

    def start(self):
        '''
        Issue a start command to the engine
        '''
        return self.__requestAndPoll('PUT', f'{baseUrl}/vehicles/v2/{self.vin}/engine/start')

    def stop(self):
        '''
        Issue a stop command to the engine
        '''
        return self.__requestAndPoll('DELETE', f'{baseUrl}/vehicles/v2/{self.vin}/engine/start')


    def lock(self):
        '''
        Issue a lock command to the doors
        '''
        return self.__requestAndPoll('PUT', f'{baseUrl}/vehicles/v2/{self.vin}/doors/lock')


    def unlock(self):
        '''
        Issue an unlock command to the doors
        '''
        return self.__requestAndPoll('DELETE', f'{baseUrl}/vehicles/v2/{self.vin}/doors/lock')

    def __makeRequest(self, method, url, data, params):
        '''
        Make a request to the given URL, passing data/params as needed
        '''

        headers = {
            **apiHeaders,
            'auth-token': self.token
        }        
    
        return getattr(requests, method.lower())(url, headers=headers, data=data, params=params)

    def __pollStatus(self, url, id):
        '''
        Poll the given URL with the given command ID until the command is completed
        '''
        status = self.__makeRequest('GET', f'{url}/{id}', None, None)
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
        command = self.__makeRequest(method, url, None, None)

        if command.status_code == 200:
            result = command.json()
            return self.__pollStatus(url, result['commandId'])
        else:
            command.raise_for_status()
