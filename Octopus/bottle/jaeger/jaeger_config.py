"""Module used to define config settings for the jaeger plugin"""

import os 
import logging 
import pydantic

LOGGER = logging.getLogger('octopus.jaeger.config')

SERVICE_NAME = os.environ.get('SERVICE_NAME')

JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))

ENABLE_JAEGER_TRACING = os.environ.get('ENABLE_JAEGER_TRACING', 'true') in ['true', 't']


class JaegerConfig(pydantic.BaseModel):
    """Dataclass used to encapsulate the config settings
    used by the prometheus plugin"""
    
    jaeger_host: str = 'localhost'
    jaeger_port: int = 6831
    
JAEGER_CONFIG = JaegerConfig(jaeger_host=JAEGER_HOST, jaeger_port=JAEGER_PORT)

def override_jaeger_config(jaeger_config: dict):
    """Helper function used to override
    config settings"""
    
    global JAEGER_CONFIG
    
    LOGGER.debug('overriding environment configurations with jaeger config')
            
    try:
        JAEGER_CONFIG = JaegerConfig(**jaeger_config)
        
    except pydantic.ValidationError as err:
        LOGGER.exception(err)
        
        raise RuntimeError('received invalid config dict for jaeger plugin')
