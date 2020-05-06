"""Module containing a series of helper functions used
to carry out the profiling of python functions"""

import logging 
import os

from Octopus.tracing import decorators
from Octopus.tracing import helpers

logger = logging.getLogger('octopus.tracing')

ENABLE_OCTOPUS = os.environ.get('ENABLE_OCTOPUS', 'false').lower() in ['true', 't']
DIRECT_OMISSIONS = os.environ.get('OCTOPUS_DIRECT_OMISSIONS').split(',')

def profiled_instance(obj: object, exclusions: list = []):
    """Helper function used to apply decorator to instance
    of an object/class"""
    
    # only apply octopus if environment variable configured to true
    if not ENABLE_OCTOPUS:
        logger.warning('octopus tracing is disabled')
        
        return obj
    
    def is_magic_method(func: str) -> bool:
        """Closure used to determine if a method is magic"""
        
        return func[:2] == '__' and func[len(func) - 2:] == '__'
    
    # get all methods that belong to instance and fillter on magic methods
    methods = [func for func in dir(obj) if callable(getattr(obj, func)) and not is_magic_method(func)]
    
    logger.info('applying octopus tracing to functions %s', ','.join(methods))
    
    for method in methods:
        if method not in DIRECT_OMISSIONS:
            setattr(obj, method, decorators.profiled_method(obj.__class__.__name__)(getattr(obj, method)))
        
    return obj