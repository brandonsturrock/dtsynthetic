import requests
import json
import re
import pandas as pd

from dtsynthetic.monitors import HTTPMonitor, BrowserMonitor, DraftHTTPMonitor, DraftBrowserMonitor

class SyntheticAPI:

    """This class is used to interact directly with the Dynatrace Synthetics API by querying existing monitors, creating new monitors, and bulk updating edited monitors
    :param tenant: A valid url for the Dynatrace tenant you wish to interact with
    :type tenant: str
    :param api_key: A valid access token for the Dynatrace tenant you wish to interact with, with synthetic v1 and v2 scopes
    :type tenant: str
    """

    def __init__(self, tenant:str, api_key:str):
        self.tenant = self.__validate_url(tenant)
        self.api_key = api_key
        self.__headers = {'Authorization' : f'Api-Token {self.api_key}', 'Content-Type' : 'application/json'}

    def new_monitor(self, data:dict):
        if data['type'] == 'HTTP':
            return DraftHTTPMonitor(data=data, request_data={'tenant' : self.tenant, 'headers' : self.__headers})
        elif data['type'] == 'BROWSER':
            return DraftBrowserMonitor(data=data, request_data={'tenant' : self.tenant, 'headers' : self.__headers})
        
    def load_simple_http_csv(self, path:str):
        df = pd.read_csv(path, low_memory=False)
        monitors = []
        for index, row in df.iterrows():
            body_check = row['Request Body']
            if pd.isnull(body_check):
                request_body = None
            else:
                request_body = body_check

            tags = []
            if len(row) > 9:
                i = 9
                while i < len(row):
                    tags.append({'key' : df.columns[i],'value' : df.iloc[index,i]})
                    i+=1

            if row['Type']=='HTTP':
                body = {
                    "name": row['Monitor Name'],
                    "frequencyMin": row['Frequency'],
                    "enabled": row['Enabled'],
                    "type": "HTTP",
                    "script": {
                        "version" : '1.0',
                        "requests": [
                        {
                            "description": row['Description'] if 'Description' in df else row['URL'],
                            "url": row['URL'],
                            "method": row['Method'],
                            "requestBody": request_body,
                            "configuration": {
                                "acceptAnyCertificate": True,
                                "followRedirects": True
                            },
                            "preProcessingScript": "",
                            "postProcessingScript": ""
                        }
                        ]
                    },
                    "locations": row['Locations'].split(','),
                    "tags": tags,
                    "manuallyAssignedApps" : []
                }
                if body['script']['requests'][0]['requestBody'] is None:
                    del body['script']['requests'][0]['requestBody']

                monitors.append(DraftHTTPMonitor(data=body, request_data={'tenant' : self.tenant, 'api_key':self.api_key, 'headers' : self.__headers}))
        
        return monitors

    def get_monitor(self, entityId:str, detailed:bool=False):
        url = self.tenant + f'/api/v1/synthetic/monitors/{entityId}'
        result = requests.get(url, headers = self.__headers)
        if result.ok:
            data = json.loads(result.content)
            if data['type'] == 'HTTP':
                new_monitor = HTTPMonitor(data, {'tenant' : self.tenant,'headers' : self.__headers}, False)
            else:
                new_monitor = BrowserMonitor(data, {'tenant' : self.tenant,'headers' : self.__headers}, False)

            if detailed: new_monitor.get_details()
            
            return new_monitor
        
        else:
            raise Exception(result.content)
        
    def update(self, monitors:list):
        success = []
        failure = []
        if not monitors: return
        for monitor in monitors:
            x = monitor.update()
            if x['status'] == 204:
                success.append(x)
            else:
                failure.append(x)
        return {    
            'success_count' : len(success),
            'failure_count' : len(failure),
            'success' : success,
            'failure' : failure
        }

    def get_monitors(self, params:dict={}, detailed:bool=False):
        url = self.tenant + '/api/v1/synthetic/monitors'

        if params:
            url = url + '?'
            if 'tags' in params:
                url = url + self.__handle_tags(params['tags'])
            if 'location' in params:
                url = url + self.__handle_location(params['location'])
            if 'type' in params:
                url = url + self.__handle_type(params['type'])
            if 'enabled' in params:
                url = url + self.__handle_enabled(params['enabled'])
            if 'assignedApps' in params:
                url = url + self.__handle_assigned_apps(params['assignedApps'])
            if 'managementZone' in params:
                url = url + self.__handle_management_zone(params['managementZone'])
            if 'credentialId' in params:
                url = url + self.__handle_credential_id(params['credentialId'])
            if 'credentialOwner' in params:
                url = url + self.__handle_credential_owner(params['credentialOwner'])

        url = url[:-1] if url[-1] == '&' else url
            
        result = requests.get(url, headers = self.__headers)
        if result.ok:
            raw_data = json.loads(result.content)['monitors']
            new_monitors = [HTTPMonitor(x, {'tenant' : self.tenant,'headers' : self.__headers}, False) if x['type'] == 'HTTP' else BrowserMonitor(x, {'tenant' : self.tenant,'headers' : self.__headers}, False) for x in raw_data]
            if detailed: [x.get_details() for x in new_monitors]
            return new_monitors
        else:
            raise Exception("Fetch failed.")
        
    def __handle_management_zone(self, managementZone:int):
        query_string = ''
        if type(managementZone) != int: raise Exception("Invalid managementZone parameter.")
        query_string = query_string + 'managementZone=' + str(managementZone) + '&'

        return query_string    
        
    def __handle_type(self, xtype:str):
        query_string = ''
        if type(xtype) != str: raise Exception("Invalid type parameter.")
        query_string = query_string + 'type=' + xtype + '&'

        return query_string
    
    def __handle_credential_id(self, credentialId:str):
        query_string = ''
        if type(credentialId) != str: raise Exception("Invalid credentialId parameter.")
        query_string = query_string + 'credentialId=' + credentialId + '&'

        return query_string

    def __handle_credential_owner(self, credentialOwner:str):
        query_string = ''
        if type(credentialOwner) != str: raise Exception("Invalid credentialOwner parameter.")
        query_string = query_string + 'credentialOwner=' + credentialOwner + '&'

        return query_string
    
    def __handle_enabled(self, enabled:bool):
        query_string = ''
        if type(enabled) != bool: raise Exception("Invalid enabled parameter.")
        query_string = query_string + 'enabled=' + str(enabled) + '&'

        return query_string
    
    def __handle_location(self, location:str):
        query_string = ''
        if type(location) != str: raise Exception("Invalid locations parameter.")
        query_string = query_string + 'location=' + location + '&'

        return query_string

    def __handle_assigned_apps(self, assigned_apps:list):
        query_string = ''
        
        if type(assigned_apps) != list: raise Exception("Invalid assignedApps parameter.")
        
        for assigned_app in assigned_apps:
            if type(assigned_app) == str:
                query_string = query_string + 'assignedApps=' + assigned_app + "&"

        return query_string

    def __handle_tags(self, tags:list):
        query_string = ''
        
        if type(tags) != list: raise Exception("Invalid tags parameter.")
        
        for tag in tags:
            if type(tag) == dict:
                query_string = query_string + 'tag=' + list(tag.keys())[0] + ':' + list(tag.values())[0] + "&"
            elif type(tag) == str:
                query_string = query_string + 'tag=' + tag + "&"
            elif type(tag) == int:
                query_string = query_string + 'tag=' + str(tag) + "&"

        return query_string
   
    def __validate_url(self, tenant:str):
        result = re.search('^https://',tenant)
        if result:
            if tenant[-1] == '/':
                return tenant[:-1]
            else:
                return tenant
        else:
            raise Exception('Invalid Tenant URL. Be sure it begins with "https://".')


