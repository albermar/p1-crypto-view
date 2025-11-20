class InfrastructureProviderNotCompatibleError(Exception):
    '''__
    Raises if the Symbol or Currency isn't supported by the asked provider
    '''
    
class InfrastructureBadURL(Exception):
    '''__
    Raises if it's impossible to execute the request due to a lack of URL, Tokens, or whatever.  
    '''
    
class InfrastructureExternalApiTimeout(Exception):
    '''__
    httpx.TimeoutException
    '''
    
class InfrastructureExternalApiError(Exception):
    '''__ 
     httpx.RequestError or non 2xx HTTP status codes from external API
    '''

    
class InfrastructureValidationError(Exception):
    '''__
    Raises if there is a validation error in the parameters sent to the external API
    '''    

class InfrastructureExternalApiMalformedResponse(Exception):
    '''__
    Raises if the response from the external API is malformed or cannot be parsed
    '''