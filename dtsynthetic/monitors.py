import requests
import json
import copy

from dtsynthetic.extras import HTTPRequest, KeystrokesEvent, NavigateEvent, CookieEvent, JavaScriptEvent, SelectOptionEvent, InteractionEvent, HTTPScript, BrowserScript

class DraftHTTPMonitor:
    def __init__(self, data:dict, request_data:dict):
        self.name = data['name']
        self.enabled = data['enabled']
        self.type = data['type']
        self.frequencyMin = data['frequencyMin']
        self.script = {'version' : data['script']['version'], 'requests' : [HTTPRequest(x) for x in data['script']['requests']]}
        self.locations = data['locations']
        self._request_data = request_data
        if 'anomalyDetection' in data: self.anomalyDetection = data['anomalyDetection']
        if 'manuallyAssignedApps' in data: self.manuallyAssignedApps = data['manuallyAssignedApps']
        else: self.manuallyAssignedApps = []
        if 'tags' in data: self.tags = data['tags']
        else: self.tags = []

    def add_tag(self, key:str, value:str=None):
        tag_already_exists = False

        for x in self.tags:
            if key == x['key']:
                tag_already_exists = True

        if not tag_already_exists and value:
            self.tags.append({'key' : key, 'value' : value})
        elif not tag_already_exists:
            self.tags.append({'key' : key})
   
        
    def data(self):
        x = dict(copy.deepcopy(vars(self)))
        x['script']['requests'] = [y.data() for y in x['script']['requests']]
        del x['_request_data']
        return x
    
    def create(self):
        url = self._request_data['tenant'] + '/api/v1/synthetic/monitors'
        body = json.dumps(self.data())
        result = requests.post(url, data=body, headers=self._request_data['headers'])
        if result.ok:
            self.entityId = json.loads(result.content)['entityId']
            return HTTPMonitor(self.data(), self._request_data, False)
        else:
            return vars(result)

class DraftBrowserMonitor:
    def __init__(self, data:dict, request_data:dict):
        self.name = data['name']
        self.frequencyMin = data['frequencyMin'] if 'frequencyMin' in data else None
        self.enabled = data['enabled']
        self.type = data['type']
        self.script = {'type' : data['script']['type'], 'version' : data['script']['version'], 'events' : [self.__classifyEvent(x) for x in data['script']['events']]}
        self.locations = data['locations']
        self._request_data = request_data
        if 'anomalyDetection' in data: self.anomalyDetection = data['anomalyDetection']
        if 'keyPerformanceMetrics' in data: self.keyPerformanceMetrics = data['keyPerformanceMetrics']
        else: self.keyPerformanceMetrics = {"loadActionKpm": "VISUALLY_COMPLETE","xhrActionKpm": "VISUALLY_COMPLETE"}
        if 'tags' in data: self.tags = data['tags']
        else: self.tags = []
        if 'configuration' in data['script']: self.script['configuration'] = data['script']['configuration']
        else: self.script['configuration'] = {}

    def add_tag(self, key:str, value:str=None):
        tag_already_exists = False

        for x in self.tags:
            if key == x['key']:
                tag_already_exists = True

        if not tag_already_exists and value:
            self.tags.append({'key' : key, 'value' : value})
        elif not tag_already_exists:
            self.tags.append({'key' : key})

    def data(self):
        x = dict(copy.deepcopy(vars(self)))
        x['script']['events'] = [y.data() for y in x['script']['events']]
        del x['_request_data']
        return x
    
    def __classifyEvent(self, event:dict):

        if event['type'] == 'navigate':
            return NavigateEvent(event)
        elif event['type'] == 'click' or event['type'] == 'tap':
            return InteractionEvent(event)
        elif event['type'] == 'javascript':
            return JavaScriptEvent(event)
        elif event['type'] == 'cookie':
            return CookieEvent(event)
        elif event['type'] == 'keystrokes':
            return KeystrokesEvent(event)
        elif event['type'] == 'selectOption':
            return SelectOptionEvent(event)
        else: raise Exception(event)
    
    def create(self):
        url = self._request_data['tenant'] + '/api/v1/synthetic/monitors'
        body = json.dumps(self.data())
        result = requests.post(url, data=body, headers=self._request_data['headers'])
        if result.ok:
            self.entityId = json.loads(result.content)['entityId']
            return BrowserMonitor(self.data(), self._request_data, False)
        else:
            return vars(result)

class HTTPMonitor:
    def __init__(self, data:dict, request_data:dict, detailed:bool):
        self.__name = data['name']
        self.__entityId = data['entityId']
        self.enabled = data['enabled']
        self.type = data['type']
        self._request_data = request_data
        if 'createdFrom' in data: self.createdFrom = data['createdFrom']
        if 'script' in data: self.script = HTTPScript(data['script']['version'],[HTTPRequest(x) for x in data['script']['requests']])
        if 'locations' in data: self.locations = data['locations']
        if 'anomalyDetection' in data: self.anomalyDetection = data['anomalyDetection']
        if 'managementZones' in data: self.managementZones = data['managementZones']
        if 'automaticallyAssignedApps' in data: self.automaticallyAssignedApps = data['automaticallyAssignedApps']
        if 'frequencyMin' in data: self.frequencyMin = data['frequencyMin']
        if 'tags' in data: self.tags = data['tags']
        self.is_detailed = detailed

    @property
    def name(self):
        return self.__name
    
    @property
    def entityId(self):
        return self.__entityId

    def get_details(self):
        url = self._request_data['tenant'] + f'/api/v1/synthetic/monitors/{self.entityId}'
        result = requests.get(url, headers = self._request_data['headers'])
        if result.ok:
            data = json.loads(result.content)
            self.createdFrom = data['createdFrom']
            self.script = HTTPScript(data['script']['version'],[HTTPRequest(x) for x in data['script']['requests']])
            self.locations = data['locations']
            self.anomalyDetection = data['anomalyDetection']
            self.managementZones = data['managementZones']
            self.automaticallyAssignedApps = data['automaticallyAssignedApps']
            self.manuallyAssignedApps = data['manuallyAssignedApps']
            self.frequencyMin = data['frequencyMin']
            self.tags = data['tags']
            self.is_detailed = True

    def update(self):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to update a script')
        url = self._request_data['tenant'] + f'/api/v1/synthetic/monitors/{self.entityId}'
        result = requests.put(url, headers = self._request_data['headers'], data = json.dumps(self.data()))
        return_data = {'status' : result.status_code,'entityId' : self.entityId, 'message' : None} if result.status_code == 204 else {'status' : result.status_code, 'entityId' : self.entityId, 'message' : result.content}

        return return_data
    
    def enable(self):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')
        if not hasattr(self, 'script'): raise Exception('Call get_details() before attempting to edit a script')
        self.enabled = True
        return self.update()

    def disable(self):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')
        if not hasattr(self, 'script'): raise Exception('Call get_details() before attempting to edit a script')
        self.enabled = False
        return self.update()
    
    def has_tag(self, key:str, value:str=None):
        if not value:
            for x in self.tags:
                if key == x['key']:
                    return True    
            return False
        else:
            for x in self.tags:
                if key == x['key'] and value == x['value']:
                    return True    
            return False              
    
    def add_tag(self, key:str, value:str=None, update:bool=False):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')
        tag_already_exists = False

        for x in self.tags:
            if key == x['key']:
                tag_already_exists = True

        if not tag_already_exists and value:
            self.tags.append({'key' : key, 'value' : value})
        elif not tag_already_exists:
            self.tags.append({'key' : key})

        if update:
            return self.update()

    def remove_tag(self, key:str, update:bool=False):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')

        for x in self.tags:
            if key == x['key']:
                self.tags.remove(x)
        if update:
            return self.update()
        
    def change_tag(self, key:str, value:str=None):
        tag = self.__find_tag(key)
        if tag:
            tag['value'] = value

    def __find_tag(self, key:str):
        for x in self.tags:
            if key == x['key']:
                return x           
        return False 
        
    def execute(self, params:dict={}):
        url = self._request_data['tenant'] + f'/api/v2/synthetic/executions/batch'
        monitor_config = {
                'monitorId' : self.entityId,
                'executionCount' : params['executionCount'] if 'executionCount' in params else 1,
                'repeatMode' : params['repeatMode'] if 'repeatMode' in params else 'SEQUENTIAL',
            }
        if 'locations' in params: monitor_config['locations'] = params['locations']
        if 'customizedScript' in params: monitor_config['customizedScript'] = params['customizedScript']
        body = {
            'processingMode': params['processingMode'] if 'processingMode' in params else 'STANDARD',
            'failOnPerformanceIssue' : params['failOnPerformanceIssue'] if 'failOnPerformanceIssue' in params else False,
            'failOnSslWarning' : params['failOnSslWarning'] if 'failOnSslWarning' in params else False,
            'stopOnProblem' : params['stopOnProblem'] if 'stopOnProblem' in params else False,
            'takeScreenshotsOnSuccess' : params['takeScreenshotsOnSuccess'] if 'takeScreenshotsOnSuccess' in params else False,
            'metadata' : params['metadata'] if 'metadata' in params else {},
            'monitors' : [monitor_config]
        }

        if self.enabled == False:
            self.enable()
            result = requests.post(url, headers = self._request_data['headers'], data = json.dumps(body))
            self.disable()
            return json.loads(result.content)
    
        result = requests.post(url, headers = self._request_data['headers'], data = json.dumps(body))
        return json.loads(result.content)

    def data(self):
        y = {}
        x = dict(copy.deepcopy(vars(self)))
        x.pop('_request_data')
        x.pop('is_detailed')
        if 'script' in x: x['script'] = x['script'].data()
        y['name'] = x['_HTTPMonitor__name']
        del x['_HTTPMonitor__name']
        y['entityId'] = x['_HTTPMonitor__entityId']
        del x['_HTTPMonitor__entityId']
        y.update(x)
        return y
       
class BrowserMonitor:
    def __init__(self, data:dict, request_data:dict, detailed:bool):
        self.__name = data['name']
        self.__entityId = data['entityId']
        self.enabled = data['enabled']
        self.type = data['type']
        self._request_data = request_data
        if 'createdFrom' in data: self.createdFrom = data['createdFrom']
        if 'script' in data: self.script = BrowserScript(data['script']['type'],data['script']['version'],[self.__classifyEvent(x) for x in data['script']['events']])
        if 'locations' in data: self.locations = data['locations']
        if 'anomalyDetection' in data: self.anomalyDetection = data['anomalyDetection']
        if 'managementZones' in data: self.managementZones = data['managementZones']
        if 'automaticallyAssignedApps' in data: self.automaticallyAssignedApps = data['automaticallyAssignedApps']
        if 'frequencyMin' in data: self.frequencyMin = data['frequencyMin']
        if 'keyPerformanceMetrics' in data: self.keyPerformanceMetrics = data['keyPerformanceMetrics']
        if 'tags' in data: self.tags = data['tags']
        self.is_detailed = detailed
    
    @property
    def name(self):
        return self.__name
    
    @property
    def entityId(self):
        return self.__entityId
    
    def enable(self):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')
        if not hasattr(self, 'script'): raise Exception('Call get_details() before attempting to edit a script')
        self.enabled = True
        return self.update()

    def disable(self):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')
        if not hasattr(self, 'script'): raise Exception('Call get_details() before attempting to edit a script')
        self.enabled = False
        return self.update()
    
    def execute(self, params:dict={}):
        url = self._request_data['tenant'] + f'/api/v2/synthetic/executions/batch'
        monitor_config = {
                'monitorId' : self.entityId,
                'executionCount' : params['executionCount'] if 'executionCount' in params else 1,
                'repeatMode' : params['repeatMode'] if 'repeatMode' in params else 'SEQUENTIAL',
            }
        if 'locations' in params: monitor_config['locations'] = params['locations']
        if 'customizedScript' in params: monitor_config['customizedScript'] = params['customizedScript']
        body = {
            'processingMode': params['processingMode'] if 'processingMode' in params else 'STANDARD',
            'failOnPerformanceIssue' : params['failOnPerformanceIssue'] if 'failOnPerformanceIssue' in params else False,
            'stopOnProblem' : params['stopOnProblem'] if 'stopOnProblem' in params else False,
            'takeScreenshotsOnSuccess' : params['takeScreenshotsOnSuccess'] if 'takeScreenshotsOnSuccess' in params else False,
            'metadata' : params['metadata'] if 'metadata' in params else {},
            'monitors' : [monitor_config]
        }

        if self.enabled == False:
            self.enable()
            result = requests.post(url, headers = self._request_data['headers'], data = json.dumps(body))
            self.disable()
            return json.loads(result.content)
    
        result = requests.post(url, headers = self._request_data['headers'], data = json.dumps(body))
        return json.loads(result.content)

    def data(self):
        y = {}
        x = dict(copy.deepcopy(vars(self)))
        x.pop('_request_data')
        x.pop('is_detailed')
        if 'script' in x: x['script'] = x['script'].data()
        y['name'] = x['_BrowserMonitor__name']
        del x['_BrowserMonitor__name']
        y['entityId'] = x['_BrowserMonitor__entityId']
        del x['_BrowserMonitor__entityId']
        y.update(x)
        return y
    
    def __classifyEvent(self, event:dict):

        if event['type'] == 'navigate':
            return NavigateEvent(event)
        elif event['type'] == 'click' or event['type'] == 'tap':
            return InteractionEvent(event)
        elif event['type'] == 'javascript':
            return JavaScriptEvent(event)
        elif event['type'] == 'cookie':
            return CookieEvent(event)
        elif event['type'] == 'keystrokes':
            return KeystrokesEvent(event)
        elif event['type'] == 'selectOption':
            return SelectOptionEvent(event)
        else: raise Exception(event)

    def update(self):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to update a script')
        url = self._request_data['tenant'] + f'/api/v1/synthetic/monitors/{self.entityId}'
        result = requests.put(url, headers = self._request_data['headers'], data = json.dumps(self.data()))
        return_data = {'status' : result.status_code,'entityId' : self.entityId} if result.status_code == 204 else {'status' : result.status_code, 'entityId' : self.entityId, 'message' : result.content}

        return return_data
        
    def get_details(self):
        url = self._request_data['tenant'] + f'/api/v1/synthetic/monitors/{self.entityId}'
        result = requests.get(url, headers = self._request_data['headers'])
        if result.ok:
            data = json.loads(result.content)
            self.createdFrom = data['createdFrom']
            self.script = BrowserScript(
                data['script']['type'],
                data['script']['version'],
                [self.__classifyEvent(x) for x in data['script']['events']]
            )
            self.locations = data['locations']
            self.anomalyDetection = data['anomalyDetection']
            self.managementZones = data['managementZones']
            self.automaticallyAssignedApps = data['automaticallyAssignedApps']
            self.manuallyAssignedApps = data['manuallyAssignedApps']
            self.frequencyMin = data['frequencyMin']
            self.keyPerformanceMetrics = data['keyPerformanceMetrics']
            self.tags = data['tags']
            self.is_detailed = True

    def has_tag(self, key:str, value:str=None):
        if not value:
            for x in self.tags:
                if key == x['key']:
                    return True    
            return False
        else:
            for x in self.tags:
                if key == x['key'] and value == x['value']:
                    return True    
            return False 
    
    def add_tag(self, key:str, value:str=None, update:bool=False):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')
        tag_already_exists = False

        for x in self.tags:
            if key == x['key']:
                tag_already_exists = True

        if not tag_already_exists and value:
            self.tags.append({'key' : key, 'value' : value})
        elif not tag_already_exists:
            self.tags.append({'key' : key})

        if update:
            return self.update()

    def remove_tag(self, key:str, update:str=False):
        if not self.is_detailed: raise Exception('Call get_details() before attempting to edit a script')

        for x in self.tags:
            if key == x['key']:
                self.tags.remove(x)
        if update:
            return self.update()
        
    def change_tag(self, key:str, value:str=None):
        tag = self.__find_tag(key)
        if tag:
            tag['value'] = value

    def __find_tag(self, key:str):
        for x in self.tags:
            if key == x['key']:
                return x           
        return False 