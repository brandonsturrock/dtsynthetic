import copy

class HTTPRequest:
        def __init__(self, request):
            self.description = request['description']
            self.url = request['url']
            self.method = request['method']
            if 'requestBody' in request: self.requestBody = request['requestBody']
            self.validation = request['validation'] if 'validation' in request else None
            self.configuration = request['configuration'] if 'configuration' in request else None
            self.preProcessingScript = request['preProcessingScript'] if 'preProcessingScript' in request else ""
            self.postProcessingScript = request['__postProcessingScript'] if '__postProcessingScript' in request else ""

        def data(self):
            body = {
                'description' : self.description,
                'url' : self.url,
                'method' : self.method,
                'validation' : self.validation,
                'configuration' : self.configuration,
                'preProcessingScript' : self.preProcessingScript,
                'postProcessingScript' : self.postProcessingScript
            }
            if hasattr(self,'requestBody'):
                body['requestBody'] = self.requestBody
            return body

class NavigateEvent:
    def __init__(self, event):
        if 'type' in event: self.type = event['type']
        if 'url' in event: self.url = event['url']
        if 'description' in event: self.description = event['description']
        if 'wait' in event: self.wait = event['wait']
        if 'validate' in event: self.validate = event['validate']
        if 'target' in event: self.target = event['target'] 
        if 'authentication' in event: self.authentication = event['authentication']
    
    def data(self):
        return dict(copy.deepcopy(vars(self)))

class InteractionEvent:
    def __init__(self, event):
        if 'type' in event: self.type = event['type']
        if 'description' in event: self.description = event['description']
        if 'button' in event: self.button = event['button']
        if 'wait' in event: self.wait = event['wait']
        if 'validate' in event: self.validate = event['validate'] 
        if 'target' in event: self.target = event['target'] 
    
    def data(self):
        return dict(copy.deepcopy(vars(self)))
    
class JavaScriptEvent:
    def __init__(self, event):
        if 'type' in event: self.type = event['type']
        if 'description' in event: self.description = event['description']
        if 'javaScript' in event: self.javascript = event['javaScript']
        if 'wait' in event: self.wait = event['wait']
        if 'target' in event: self.target = event['target']
    
    def data(self):
        return dict(copy.deepcopy(vars(self)))
    
class SelectOptionEvent:
    def __init__(self, event):
        if 'type' in event: self.type = event['type']
        if 'description' in event: self.description = event['description']
        if 'selections' in event: self.selections = event['selections']
        if 'wait' in event: self.wait = event['wait']
        if 'validate' in event: self.validate = event['validate']
        if 'target' in event : self.target = event['target']
    
    def data(self):
        return dict(copy.deepcopy(vars(self)))
    
class CookieEvent:
    def __init__(self, event):
        if 'type' in event: self.type = event['type']
        if 'description' in event: self.description = event['description']
        if 'cookies' in event: self.cookies = event['cookies']
    
    def data(self):
        return dict(copy.deepcopy(vars(self)))
    
class KeystrokesEvent:
    def __init__(self, event):
        if 'type' in event: self.type = event['type']
        if 'description' in event: self.description = event['description']
        if 'textValue' in event: self.textValue = event['textValue']
        if 'masked' in event: self.masked = event['masked']
        if 'simulateBlurEvent' in event: self.simulateBlurEvent = event['simulateBlurEvent']
        if 'wait' in event: self.wait = event['wait']
        if 'validate' in event: self.validate = event['validate']
        if 'target' in event: self.target = event['target']
    
    def data(self):
        return dict(copy.deepcopy(vars(self)))

class HTTPScript:
    def __init__(self, version, requests):
        self.version = version
        self.requests = requests

    def data(self):
        return {
            'version' : self.version,
            'requests' : [x.data() for x in self.requests]
        }

    def add_request(self, url, description, method, params=None):
        new_request = {
            'url' : url,
            'description' : description,
            'method' : method
        }
        if params:
            if 'requestBody' in params: new_request['requestBody'] = params['requestBody']
            if 'validation' in params: new_request['validation'] = params['validation']
            if 'configuration' in params: new_request['configuration'] = params['configuration']
            if 'validation' in params: new_request['validation'] = params['validation']
            if 'preProcessingScript' in params: new_request['preProcessingScript'] = params['preProcessingScript']
            if 'postProcessingScript' in params: new_request['postProcessingScript'] = params['postProcessingScript']
        
        self.requests.append(HTTPRequest(new_request))

class BrowserScript:
    def __init__(self, type, version, events):
        self.type = type
        self.version = version
        self.events = events
    def data(self):
        return {
            'type' : self.type,
            'version' : self.version,
            'events' : [x.data() for x in self.events]
        }  