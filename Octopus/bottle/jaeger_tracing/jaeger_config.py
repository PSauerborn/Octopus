"""Module used to define config settings for the jaeger plugin"""

import os 
import logging 
import pydantic

LOGGER = logging.getLogger('octopus.bottle.jaeger_tracing')

SERVICE_NAME = os.environ.get('SERVICE_NAME', None)

JAEGER_HOST = os.environ.get('JAEGER_HOST', None)
JAEGER_PORT = os.environ.get('JAEGER_PORT', None)

ENABLE_JAEGER_TRACING = os.environ.get('ENABLE_JAEGER_TRACING', 'false') in ['true', 't']
ENABLE_JAEGER_WITH_PROMETHEUS = os.environ.get('ENABLE_JAEGER_WITH_PROMETHEUS', 'false') in ['true', 't']


class JaegerConfig(pydantic.BaseModel):
    """Dataclass used to encapsulate the config settings
    used by the Jaeger Tracing plugin
    
    Arguments:
        jaeger_host: str host of jaeger agent
        jaeger_port: int port of jaeger agent
        service_name: str service name of application
    """
    
    service_name: str
    jaeger_host: str = 'localhost'
    jaeger_port: int = 6831
    
JAEGER_CONFIG = None

def set_jaeger_config(jaeger_config: dict):
    """Helper function used to set the jaeger configuration (host and port) 
    for the Jaeger Tracing plugin. Note that the plugin will override any
    configuration settings passed in code with set environment variables
    
    Arguments:
        jaeger_config: dict configuration settings containing host and port
    """
    
    global JAEGER_CONFIG
      
    # override jaeger host with environment variable if set
    if JAEGER_HOST is not None:
        LOGGER.debug('jaeger host set in environment variables. overriding config with %s', JAEGER_HOST)
        jaeger_config['jaeger_host'] = JAEGER_HOST
    
    # override jaeger port with environment variable if set
    if JAEGER_PORT is not None:
        LOGGER.debug('jaeger port set in environment variables. overriding config with %s', JAEGER_PORT)
        jaeger_config['jaeger_port'] = JAEGER_PORT
    
    # override service name with environment variable if set  
    if SERVICE_NAME is not None:
        LOGGER.debug('service name set in environment variables. overriding config with %s', SERVICE_NAME)
        jaeger_config['service_name'] = SERVICE_NAME
        
    LOGGER.info('overriding default jaeger tracing configuration with %s', jaeger_config)
            
    try:
        JAEGER_CONFIG = JaegerConfig(**jaeger_config)
        
    except pydantic.ValidationError as err:
        LOGGER.exception(err.json())
        
        raise RuntimeError('received invalid config dict for jaeger plugin')
