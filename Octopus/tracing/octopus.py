"""Module containing a series of helper functions used
to carry out the profiling of python functions"""

import logging 

from Octopus.tracing import decorators

logger = logging.getLogger('octopus.tracing')

def profiled_instance(obj: object, exclusions: list = []):
    """Helper function used to apply decorator to instance
    of an object/class"""
    
    def is_magic_method(func: str) -> bool:
        """Closure used to determine if a method is magic"""
        
        return func[:2] == '__' and func[len(func) - 2:] == '__'
    
    # get all methods that belong to instance and fillter on magic methods
    methods = [func for func in dir(obj) if callable(getattr(obj, func)) and not is_magic_method(func)]
    
    logger.info('Applying Jaeger Tracing to functions %s', ','.join(methods))
    
    for method in methods:
        setattr(obj, method, decorators.profiled_method(getattr(obj, method)))
    
    return obj
