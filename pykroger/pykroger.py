import requests
import json
import base64
import numpy as np

class Kroger:
    def __init__(self):
        """
        Need to implement a circumvention of pagination.

        PARAMETERS
            fmt [bool]: Determines whether output is formatted. 
            True returns formatted, False returns raw information from request.
        """
        self.__auth_url = 'https://api.kroger.com/v1/connect/oauth2/token'
        self.__locations_url = 'https://api.kroger.com/v1/locations'
        self.__products_url = 'https://api.kroger.com/v1/products'
        self.__chains_url = 'https://api.kroger.com/v1/chains'
        # self.__departments_url = 'https://api.kroger.com/v1/departments' # not implemented
        self.__client_id = None
        self.__client_secret = None
        self.__access_token = None

    def __b64enc(self,string):
        return base64.b64encode(string.encode('utf8')).decode('utf8')

    def authenticate(self,client_id,client_secret):
        """
        DESCRIPTION
            Authentication for the first time without access token.

        PARAMETERS 
            client_id [str]: client_id provided by kroger developers portal
            client_secret [str]: client_secret provided by kroger developers portal

        MORE INFORMATION
            To obtain a client_id and client_secret, you can register your application at:
            https://www.developer.kroger.com
            If you are do not know how to set up an application, you can read this tutorial:
            <insert medium tutorial here later>
        """
        self.__client_id = client_id
        self.__client_secret = client_secret
        headers = {'Content-Type':'application/x-www-form-urlencoded',
            'Authorization':"Basic {}".format(self.__b64enc('{}:{}'.format(client_id,client_secret)))}
        data = {"grant_type":"client_credentials","scope":"product.compact"}
        response = requests.post(self.__auth_url,headers=headers,data=data)
        if response.status_code == 500:
            raise Exception('ERROR: Internal server error')
        elif response.status_code == 400:
            error_description = json.loads(response.text)['error_description']
            raise Exception('ERROR: {}'.format(error_description))
        elif response.status_code == 200:
            self.__access_token = json.loads(response.text)['access_token']

    def reauthenticate(self,access_token):
        """
        DESCRIPTION
            Authentication with saved access token. 
            This function does not check if the access is valid.

        PARAMETERS
            access_token [str]: access_token provided by authorization process

        MORE INFORMATION
            You should use this function if you have previously authenticated and saved
            your access token with the .view_access_token() method. Note that access tokens
            only remain valid for 30 minutes. [This needs a fact check, I'm not positive it is
            30 minutes. Valid time is 1800, which I assume refers to seconds.]
        
        """
        self.__access_token = access_token


    def view_client_id(self):
        "Allows you to view client id if authentication complete"
        assert self.__client_id != None, 'ERROR: No client ID available'
        return self.__client_id
    
    def view_client_secret(self):
        "Allows you to view client secret if authentication complete."
        assert self.__client_secret != None, 'ERROR: No client secret available'
        return self.__client_secret

    def view_access_token(self):
        "Allows you to view access token if authentication complete."
        assert self.__access_token != None, 'ERROR: No access token available'
        return self.__access_token

    def _get_location(self,headers,params):
        response = requests.get(self.__locations_url,headers=headers,params=params)
        if response.status_code == 400:
            raise Exception('400 ERROR: {}'.format(json.loads(response.text)['reason']))
        elif response.status_code == 401:
            raise Exception('401 ERROR: {}'.format(json.loads(response.text)['error_description']))
        elif response.status_code == 404:
            raise Exception('404 ERROR: {}'.format('404 not found'))
        elif response.status_code == 500:
            raise Exception('500 ERROR: {}'.format(json.loads(response.text)['reason']))
        elif response.status_code == 200:
            return json.loads(response.text)


    def location_list_by_zip(self,zip_code=None,radius=None,limit=None,chain=None):
        """
        
        """
        assert self.__access_token != None, 'ERROR: Not yet authenticated'
        assert zip_code != None, 'ERROR: You must enter a zip code'
        param_dict = {'filter.zipCode.near':zip_code,
                    'filter.radiusInMiles':radius,
                    'filter.limit':limit,
                    'filter.chain':chain}
        headers = {'Accept':'application/json','Authorization':'Bearer {}'.format(self.__access_token)}
        params = tuple([(k,v) for k,v in param_dict.items() if v != None])
        return self._get_location(headers,params)

    def location_list_by_coords(self,lat=None,lon=None,radius=None,limit=None,chain=None):
        """
        
        """
        assert self.__access_token != None, 'ERROR: Not yet authenticated'
        assert lat != None, 'ERROR: You must enter a latitude'
        assert lon != None, 'ERROR: You must enter a longitude'
        param_dict = {'filter.lat.near':lat,
                    'filter.lon.near':lon,
                    'filter.radiusInMiles':radius,
                    'filter.limit':limit,
                    'filter.chain':chain}
        headers = {'Accept':'application/json','Authorization':'Bearer {}'.format(self.__access_token)}
        params = tuple([(k,v) for k,v in param_dict.items() if v != None])
        return self._get_location(headers,params)

    def location_details(self,location_id):
        pass

    def location_query(self,location_id):
        pass

    def chain_list(self):
        """
        Provides a list of all chains owned by Kroger
        """
        headers = {'Accept':'application/json','Authorization':'Bearer {}'.format(self.__access_token)}
        response = requests.get(self.__chains_url,headers=headers)
        if response.status_code == 401:
            raise Exception('ERROR: {}'.format(json.loads(response.text)['error_description']))
        elif response.status_code == 500:
            raise Exception('ERROR: {}'.format(json.loads(response.text)['reason']))
        elif response.status_code == 200:
            return json.loads(response.text)

    def chain_details(self,chain):
        'Not Implemented Yet'
        raise Exception('Not Implemented Yet')

    def chain_query(self,chain):
        'Not Implemented Yet'
        raise Exception('Not Implemented Yet')

    def department_list(self):
        'Not Implemented Yet'
        raise Exception('Not Implemented Yet')

    def department_details(self,id):
        'Not Implemented Yet'
        raise Exception('Not Implemented Yet')

    def department_query(self,id):
        'Not Implemented Yet'
        raise Exception('Not Implemented Yet')

    def product_search(self,term=None,location_id=None,product_id=None,brand=None,fulfillment=None,start=None,limit=None):
        assert term != None, 'ERROR: You must at least include a search term'
        headers = {'Accept':'application/json','Authorization':'Bearer {}'.format(self.__access_token)}
        param_dict = {'filter.term':term,
                    'filter.locationId':location_id,
                    'filter.product_id':product_id,
                    'filter.brand':brand,
                    'filter.fulfillment':fulfillment,
                    'filter.start':start,
                    'filter.limit':limit}
        params = tuple([(k,v) for k,v in param_dict.items() if v != None])
        response = requests.get(self.__products_url,headers=headers,params=params)
        if response.status_code == 400:
            raise Exception('400 ERROR: {}'.format(json.loads(response.text)['reason']))
        elif response.status_code == 401:
            raise Exception('401 ERROR: {}'.format(json.loads(response.text)['error_description']))
        elif response.status_code == 403:
            raise Exception('403 ERROR: {}'.format(json.loads(response.text)['reason']))
        elif response.status_code == 500:
            raise Exception('500 ERROR: {}'.format(json.loads(response.text)['reason']))
        elif response.status_code == 200:
            return json.loads(response.text)

    def product_details(self,product_id,location_id):
        'Not Implemented Yet'
        raise Exception('Not Implemented Yet')




