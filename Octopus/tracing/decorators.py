"""Module containing a series of decorators used by the tracing
module"""

import logging 
import datetime 

from Octopus.tracing import jaeger

logger = logging.getLogger('octopus.decorators')


def profiled_method(func: object):
    """Basic decorator used to profile a method call"""
    def wrapper(*args: tuple, **kwargs: dict):
        
        parent_scope = jaeger.get_active_scope()
        
        if parent_scope:
            
            logger.debug('Using active parent scope to trace')
            
            with jaeger.TRACER.start_active_span(func.__name__, child_of=parent_scope.span) as scope:
                
                scope.span.set_tag('start_timestamp', datetime.datetime.utcnow().isoformat())
                
                result = func(*args, **kwargs)
                
                scope.span.set_tag('finish_timestamp', datetime.datetime.utcnow().isoformat())
        else:
            
            logger.debug('Creating new scope for tracing')
            
            with jaeger.TRACER.start_active_span(func.__name__) as scope:
                
                scope.span.set_tag('start_timestamp', datetime.datetime.utcnow().isoformat())
                
                result = func(*args, **kwargs)
                
                scope.span.set_tag('finish_timestamp', datetime.datetime.utcnow().isoformat())
            
        return result
    return wrapper 


