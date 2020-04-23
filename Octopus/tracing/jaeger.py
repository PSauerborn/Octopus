"""Module containing functions and classes used
to connect to the jaeger service"""

import logging 
import os

import opentracing
import jaeger_client

logger = logging.getLogger('octopus.jaeger')


def get_tracer() -> jaeger_client.Config: # pragma: no cover
    """Function used to retrieve Jaeger Tracer.
    The Jaeger Host and Port can be specified in
    the environment variables, else the default
    connection to localhost at UDP port 6831
    will be used"""

    service_name = os.environ.get('SERVICE_NAME')
    
    logger.info('Getting Tracer for service %s', service_name)

    jaeger_config = {
        'sampler': {
            'type': 'const',
            'param': 1
        },
        'logging': True
    } 
    
    # get jaeger host and port from environment variables
    jaeger_host, jaeger_port = os.environ.get('JAEGER_HOST', 'localhost'), os.environ.get('JAEGER_PORT', 6831)

    logger.debug('Creating Jaeger Tracer for %s:%s', jaeger_host, jaeger_port)

    jaeger_config['local_agent'] = {'reporting_host': jaeger_host, 'reporting_port': int(jaeger_port)}

    # create jaeger client config object and return tracer
    _config = jaeger_client.Config(config=jaeger_config, service_name=service_name, validate=True)

    return _config.initialize_tracer()

class TracerProxy:
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
    
TRACER = TracerProxy()

def get_active_scope() -> object: # pragma: no cover
    """Function used to return the current
    active scope. If no current scope exists
    i.e. if tracing is disabled, None is returned
    
    Returns
        instance of opentracing.LocalThreadManager

    """

    return TRACER.scope_manager.active