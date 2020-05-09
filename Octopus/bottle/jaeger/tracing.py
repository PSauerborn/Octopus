"""Module containing functions used to trace API calls
end to end. All functions in the module use OpenTracing
framework in conjuction with a Jaeger server to provide
comprehensice API Tracing Capabilites"""

import logging
import json
import datetime
import sys

import opentracing

import requests
import bottle
import jaeger_client

from Octopus.bottle.jaeger.jaeger_config import JAEGER_CONFIG, SERVICE_NAME, ENABLE_JAEGER_TRACING

# set logger
LOGGER = logging.getLogger('octopus.jaeger.tracing')

#########################################
# Define function used to generate tracer
#########################################

def get_tracer() -> jaeger_client.Config: # pragma: no cover
    """Function used to retrieve Jaeger Tracer.
    The Jaeger Host and Port can be specified in
    the environment variables, else the default
    connection to localhost at UDP port 6831
    will be used"""

    LOGGER.info('getting jaeger tracer for service %s', SERVICE_NAME)

    jaeger_config = {
        'sampler': {
            'type': 'const',
            'param': 1
        },
        'logging': True
    } 
    
    LOGGER.debug('Creating Jaeger Tracer for %s:%s', JAEGER_CONFIG.jaeger_host, JAEGER_CONFIG.jaeger_port)

    jaeger_config['local_agent'] = {
        'reporting_host': JAEGER_CONFIG.jaeger_host, 
        'reporting_port': JAEGER_CONFIG.jaeger_port
    }

    # create jaeger client config object and return tracer
    _config = jaeger_client.Config(config=jaeger_config, service_name=SERVICE_NAME, validate=True)

    return _config.initialize_tracer()

#####################################
# define getter for tracer for module
#####################################

class Tracer:
    """Wrapper used to lazy loading of Jaeger Tracing object.
    The Jaeger Tracer will not initialize until an attribute
    of the tracer is directly referenced"""
    
    _tracer = None
    
    def initialize(self):
        self._tracer = get_tracer()
    
    def __getattr__(self, attr):
        
        if not self._tracer:
            self._tracer = get_tracer()
            
        return getattr(self._tracer, attr)
    
    def __repr__(self):
        return self._tracer.__repr__()

    def __str__(self):
        return str(self._tracer)
    
TRACER = Tracer()
    
###########################################################
# Define functions to inject and extract spans from headers
###########################################################

def get_active_scope() -> object: # pragma: no cover
    """Function used to return the current
    active scope. If no current scope exists
    i.e. if tracing is disabled, None is returned
    
    Returns
        instance of opentracing.LocalThreadManager

    """

    if ENABLE_JAEGER_TRACING:
        return TRACER.scope_manager.active

# create mappings between request methods and string
request_mappings = {
    requests.post: 'POST',
    requests.get: 'GET',
    requests.patch: 'PATCH',
    requests.put: 'PUT',
    requests.delete: 'DELETE',
    requests.options: 'OPTIONS'
}

def inject_span(request_func: object, url: str, span: object, headers: dict) -> dict:
    """Function used to inject the into the 
    header of a request. This allows requests 
    to be traced across several API's

    Arguments:
        request_func: requests function used to execute request
        url: string giving request url
        span: span object to inject into header
        headers: dictionary of headers

    Returns
        dictionary containing headers

    """

    # set tags on span
    span.set_tag(opentracing.ext.tags.HTTP_METHOD, request_mappings[request_func])
    span.set_tag(opentracing.ext.tags.HTTP_URL, url)
    span.set_tag(opentracing.ext.tags.SPAN_KIND, opentracing.ext.tags.SPAN_KIND_RPC_CLIENT)

    TRACER.inject(span, opentracing.Format.HTTP_HEADERS, headers)

    return headers

def extract_span(headers: dict) -> object:
    """Function used to extract span from headers
    dictionary
    
    Arguments:
        headers: dictionary containing headers

    Returns:
        parent: parent span
        span_tags: tags associated with Span

    """

    # extract parent span
    parent = TRACER.extract(opentracing.Format.HTTP_HEADERS, headers)

    # extract current spans and tag as server type
    span_tags = {opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_SERVER}

    return parent, span_tags

##############################################################
# Define Traced Request function used to make a traced request
##############################################################

def traced_request(request_function: object, url: str, *args: tuple, **kwargs: dict) -> bottle.response:
    """Function used to make a traced HTTP request
    via the Python requests library. If tracing is enabled,
    the request is executed within the local Span object; 
    additionally, the local span object is embedded into
    the request headers, which allows the request to be traced 
    via the Jaeger tracer. If tracing is disabled, the request 
    is carried out as normal.
    
    Arguments:
        request_function: function from requests library used to make
            HTTP request
        url: string givin URL 
    
    Returns:
        instance of bottle.response giving response from 
            server
    """
    
    # if tracing is enabled, get parent span
    parent_scope = get_active_scope()

    # if no active spans are found, carry out request without trace
    if not parent_scope:
        return request_function(url, *args, **kwargs)
    
    # inject current span into headers
    kwargs['headers'] = inject_span(request_function, url=url, span=parent_scope.span, headers=kwargs.get('headers', {}))

    with TRACER.start_active_span(url, child_of=parent_scope.span) as scope:
        
        # set tags on span
        scope.span.set_tag(opentracing.ext.tags.HTTP_METHOD, request_mappings.get(request_function, None))
        scope.span.set_tag(opentracing.ext.tags.HTTP_URL, url)
        scope.span.set_tag(opentracing.ext.tags.SPAN_KIND, opentracing.ext.tags.SPAN_KIND_RPC_CLIENT)
        
        result = request_function(url, *args, **kwargs)

    return result

#########################################
# define function used to set common tags
#########################################

common_tags = ['success', 'http_code', 'internal_code', 'message', 'msg']

def set_common_tags(span: object, result: object):
    """Function used to set a series of common tags
    to a span object"""
        
    if not isinstance(result, dict):
        return span 
    
    for key, val in result.items():
        if key.lower() in common_tags:
            span.set_tag(key, val)
    
    return span

########################################
# Define decoratosr used to trace routes
########################################

def trace(route_name):
    """Decorator used to trace basic routes. The 
    decorator works by extracing the current active
    span from any incoming requests; all functions
    and further requests are then executed in the context
    of the extracted span. If no span is present in the
    incoming request headers, the wrapper will create a new
    span and execute all functions and request in the context
    of the newly created span.
    
    Arguments:
        route_name: string giving name of route

    Returns:
        wrapped callback function
        
    """

    def decorator(func):
        def wrapper(*args, **kwargs):

            LOGGER.debug(f'Starting Trace for {route_name}')
            
            request_method = bottle.request.method 
            
            # user ID from header if present
            user_id = bottle.request.headers.get('X-Authenticated-Userid', None)

            # extract parent span
            parent, _ = extract_span(bottle.request.headers)

            # if parent exists, use parent span
            if parent:
                LOGGER.debug('Tracing - Using Parent Span')

                with TRACER.start_active_span(f'{request_method.upper()} - {route_name}', child_of=parent) as scope:
                    
                    if user_id:
                        scope.span.set_tag('user', user_id)
                        
                    scope.span.set_tag(opentracing.ext.tags.HTTP_METHOD, bottle.request.method)
                    scope.span.set_tag(opentracing.ext.tags.HTTP_URL, bottle.request.path)
                        
                    result = func(*args, **kwargs)
                    
                    # set common tags such as success, http code etc
                    set_common_tags(scope.span, result)

            # else start new span
            else:
                LOGGER.debug('Tracing - Creating New Span')

                # create span and evaluate function
                with TRACER.start_active_span(f'{request_method.upper()} - {route_name}') as scope:
                    
                    if user_id:
                        scope.span.set_tag('user', user_id)
                        
                    scope.span.set_tag(opentracing.ext.tags.HTTP_METHOD, bottle.request.method)
                    scope.span.set_tag(opentracing.ext.tags.HTTP_URL, bottle.request.path)

                    result = func(*args, **kwargs)
                    
                    # set common tags such as success, http code etc
                    set_common_tags(scope.span, result)

            return result
        return wrapper
    return decorator
