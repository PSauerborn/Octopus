"""Module containing metrics from prometheus server"""

import logging 
import time 

import bottle 

import prometheus_client
from prometheus_client import multiprocess

import Octopus.bottle.prometheus.prometheus_config as config
import Octopus.bottle.prometheus.prometheus_helpers as prometheus_helpers

LOGGER = logging.getLogger('octopus.bottle.prometheus')

###################################################
# Define code used to create registry via the proxy
###################################################

def get_prometheus_registry():
    """Function used to create prometheus registry. The
    registry is created in Multiprocessing mode if the 
    PROMETHEUS_MULTIPROC_DIR is set in the environment variables.
    Note that this requires the directory to be created on the 
    host
    
    Returns:
        Prometheus CollectorRegistry object used to store metrics
    """
    
    if config.PROMETHEUS_MULTIPROC_DIR is not None:
        LOGGER.debug('using multiprocessing mode with directory %s', config.PROMETHEUS_MULTIPROC_DIR)
        
        # create global metric registry and convert to multiprocess registry
        registry = prometheus_client.CollectorRegistry()
        
        multiprocess.MultiProcessCollector(registry)
    else:
        LOGGER.warning('multiprocessing directory not set, using default metrics registry. pre-forked and multiprocessing servers will not gather metrics correctly')
        
        registry = prometheus_client.REGISTRY
    
    return registry

class PrometheusRegistryProxy:
    """Registry proxy used to allow lazy creation of Prometheus
    metrics. The Proxy ensures that the Registry Object can be 
    instantiated at runtime, but the actual registry is only 
    created once accessed"""
    
    _registry = None
    
    def __getattr__(self, attr):
        if self._registry is None:
            self._registry = get_prometheus_registry()

        return getattr(self._registry, attr)
    
REGISTRY = PrometheusRegistryProxy()

###########################################
# Define code used to wrap bottle callbacks
###########################################

IN_PROGRESS = prometheus_client.Gauge('inprogress_requests', 'number of requests currently being processed', ['service'], multiprocess_mode='livesum')
REQUEST_COUNT = prometheus_client.Counter('http_requests_total', 'total number of incoming requests', ['method', 'endpoint', 'service', 'user', 'http_code'])
REQUEST_LATENCY = prometheus_client.Summary('http_request_latency', 'request latency', ['endpoint', 'service'])

def get_prometheus_metrics():
    """Handler function used to retrieve prometheus metrics
    from the global Prometheus registry. Metrics are served
    on the /metrics route and are scraped by the prometheus
    server"""
    
    # check authorization header if specified in config settings
    if config.PROMETHEUS_CONFIG.enable_prometheus_auth:
        LOGGER.debug('received request to /metrics route. checking authorization token')
        
        token = bottle.request.headers.get('Authorization', None)
        
        if not prometheus_helpers.is_authenticated_user(token):
            LOGGER.warning('received unauthorized request to /metrics route')
            
            bottle.response.status = 401
            
            return {'http_code': 401, 'message': 'unauthorized'}
            
    return prometheus_client.generate_latest(REGISTRY)

def prometheus_in_progress_requests(func: object):
    """Decorator used to track in progress requests.
    The decorator executes the function in the context
    of the IN_PROGRESS gauge, which increments when
    the function starts and decrements when the function
    is finished"""
    
    def wrapper(*args, **kwargs):
        
        with IN_PROGRESS.labels(service=config.PROMETHEUS_CONFIG.service_name).track_inprogress():
            result = func(*args, **kwargs)
            
        return result
    return wrapper
    
def prometheus_request_counter(func: object):
    """Decorator used to increment the prometheus
    request counter during each request. This allows
    the request rate to be calculated and aggregated
    on the prometheus server"""
    
    def wrapper(*args: tuple, **kwargs: dict):
        
        request_method, route = bottle.request.method, bottle.request.path
        
        result = func(*args, **kwargs)
        
        user = bottle.request.headers.get('X-Authenticated-Userid', 'none')
        
        http_code = bottle.response.status
        
        REQUEST_COUNT.labels(method=request_method, endpoint=route, service=config.PROMETHEUS_CONFIG.service_name, user=user, http_code=http_code).inc()
        
        return result
    return wrapper

def prometheus_request_latency(func: object):
    """Decorator used to increment the prometheus
    request counter during each request. The latency
    is measured in seconds for each route, which can 
    then be aggregated on the prometheus server"""
    
    def wrapper(*args: tuple, **kwargs: dict):
        
        with REQUEST_LATENCY.labels(endpoint=bottle.request.path, service=config.PROMETHEUS_CONFIG.service_name).time():
            result = func(*args, **kwargs)
        
        return result
    return wrapper
        