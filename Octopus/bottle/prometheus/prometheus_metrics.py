"""Module containing metrics from prometheus server"""

import logging 
import time 

import bottle 

import prometheus_client
from prometheus_client import multiprocess

from Octopus.bottle.prometheus.prometheus_config import ENABLE_PROMETHEUS_METRICS, SERVICE_NAME, PROMETHEUS_MULTIPROC_DIR

LOGGER = logging.getLogger('octopus.prometheus.metrics')

###################################################
# Define code used to create registry via the proxy
###################################################

def get_prometheus_registry():
    """Function used to create prometheus registry"""
    
    # create global metric registry and convert to multiprocess registry
    registry = prometheus_client.CollectorRegistry()
    
    if PROMETHEUS_MULTIPROC_DIR is not None:
        LOGGER.debug('using multiprocessing mode with directory %s', PROMETHEUS_MULTIPROC_DIR)
        
        multiprocess.MultiProcessCollector(registry)
    
    return registry

class PrometheusRegistryProxy:
    """Registry proxy used to allow lazy creation of prometheus
    registry"""
    
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
REQUEST_COUNT = prometheus_client.Counter('http_requests_total', 'total number of incoming requests', ['method', 'endpoint', 'service'])
REQUEST_LATENCY = prometheus_client.Summary('http_request_latency', 'request latency', ['endpoint', 'service'])

def get_prometheus_metrics():
    """Handler function used to retrieve prometheus metrics"""
    
    return prometheus_client.generate_latest(REGISTRY)

def prometheus_in_progress_requests(func: object):
    """Decorator used to track in progress requests"""
    def wrapper(*args, **kwargs):
        
        with IN_PROGRESS.labels(service=SERVICE_NAME).track_inprogress():
            result = func(*args, **kwargs)
            
        return result
    return wrapper
    
def prometheus_request_counter(func: object):
    """Decorator used to increment the prometheus
    request counter during each request"""
    def wrapper(*args: tuple, **kwargs: dict):
        
        request_method, route = bottle.request.method, bottle.request.path
        
        REQUEST_COUNT.labels(method=request_method, endpoint=route, service=SERVICE_NAME).inc()
        
        return func(*args, **kwargs)
    return wrapper

def prometheus_request_latency(func: object):
    """Decorator used to increment the prometheus
    request counter during each request"""
    def wrapper(*args: tuple, **kwargs: dict):
        
        with REQUEST_LATENCY.labels(endpoint=bottle.request.path, service=SERVICE_NAME).time():
            result = func(*args, **kwargs)
        
        return result
    return wrapper
        