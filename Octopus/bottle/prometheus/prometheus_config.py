"""Module containing settings used for the Prometheus
bottle plugin"""

import logging 
import os
import pydantic
import typing

import Octopus.bottle.prometheus.prometheus_exceptions as exceptions

LOGGER = logging.getLogger('octopus.bottle.prometheus')

ENABLE_PROMETHEUS_METRICS = os.environ.get('ENABLE_PROMETHEUS_METRICS', 'false').lower() in ['true', 't']
PROMETHEUS_MULTIPROC_DIR = os.environ.get('prometheus_multiproc_dir', None)
PROMETHEUS_METRICS = os.environ.get('PROMETHEUS_METRICS', None)

SERVICE_NAME = os.environ.get('SERVICE_NAME', None)

ENABLE_PROMETHEUS_AUTH = os.environ.get('ENABLE_PROMETHEUS_AUTH', None)
PROMETHEUS_AUTH_TOKEN = os.environ.get('PROMETHEUS_AUTH_TOKEN', None)


class PrometheusConfig(pydantic.BaseModel):
    """Dataclass used to encapsulate the config settings
    used by the prometheus plugin
    
    Arguments:
        service_name: str name of service 
        metrics: list metrics list to deliver. Currently supported
            metrics are ['latency', 'request_count', 'processing_requests']
    """
    
    service_name: str
    enable_prometheus_auth: bool = False
    prometheus_auth_token: str = ''
    metrics: typing.List[str] = ['latency', 'request_count', 'processing_requests']
    
PROMETHEUS_CONFIG = None

def set_prometheus_config(prometheus_config: dict):
    """Helper function used to set the prometheus configuration (host and port) 
    for the prometheus Tracing plugin. Note that the plugin will override any
    configuration settings passed in code with set environment variables
    
    Arguments:
        prometheus_config: dict configuration settings containing host and port
    """
    
    global PROMETHEUS_CONFIG
      
    # override prometheus host with environment variable if set
    if SERVICE_NAME is not None:
        LOGGER.debug('service name set in environment variables. using %s', SERVICE_NAME)
        prometheus_config['service_name'] = SERVICE_NAME
    
    if ENABLE_PROMETHEUS_AUTH is not None:
        LOGGER.debug('enable_prometheus_auth set in environment variables. using %s', ENABLE_PROMETHEUS_AUTH)
        prometheus_config['enable_prometheus_auth'] = ENABLE_PROMETHEUS_AUTH
        
    if PROMETHEUS_AUTH_TOKEN is not None:
        LOGGER.debug('prometheus_auth_token set in environment variables. using %s', PROMETHEUS_AUTH_TOKEN)
        prometheus_config['prometheus_auth_token'] = PROMETHEUS_AUTH_TOKEN
        
    if PROMETHEUS_METRICS is not None:
        LOGGER.debug('prometheus_metrics set in environment variables. using %s', PROMETHEUS_METRICS.split(','))
        prometheus_config['metrics'] = PROMETHEUS_METRICS.split(',')
        
    LOGGER.info('overriding default prometheus tracing configuration with %s', prometheus_config)
            
    try:
        PROMETHEUS_CONFIG = PrometheusConfig(**prometheus_config)
        
        # raise exception if prometheus authentication is enabled and token is not provided
        if PROMETHEUS_CONFIG.enable_prometheus_auth and not PROMETHEUS_CONFIG.prometheus_auth_token:
            raise exceptions.PrometheusConfigurationException('prometheus authorization enabled but token not provided')
        
    except pydantic.ValidationError as err:
        LOGGER.exception(err.json())
        
        raise exceptions.PrometheusConfigurationException('received invalid config dict for prometheus plugin')

