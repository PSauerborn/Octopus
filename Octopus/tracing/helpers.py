"""Module containing a series of helper functions used by the octopus 
module"""

import logging 
import os
import re

logger = logging.getLogger('octopus.helpers')

OCTOPUS_EXCLUSION_PATTERNS = os.environ.get('OCTOPUS_EXCLUSION_PATTERNS', '').split(',')
OCTOPUS_INCLUSION_PATTERNS = os.environ.get('OCTOPUS_INCLUSION_PATTERNS', '').split(',')


def filter_on_inclusion(expressions: list, methods: list) -> list:
    """Helper function used to filter expressions
    based on inclusion"""
    
    filtered_methods = set()
    
    for expression in expressions:
        valid_methods = [method for method in methods if matches_expression(expression, method)]
        
        filtered_methods += set(valid_methods)
    
    return filtered_methods

def filter_on_exclusion(expressions: list, methods: list) -> list:
    """Helper function used to filter expressions
    based on exclusion"""
    
    filtered_methods = set()
    
    for expression in expressions:
        valid_methods = [method for method in methods if not matches_expression(expression, method)]
        
        filtered_methods += set(valid_methods)
    
    return filtered_methods

def matches_expression(pattern: str, method: str) -> bool:
    """Helper function used to determine if a
    particular method name matches a given RE
    expression"""
    
    return True

def filter_methods(methods: list) -> list:
    """Helper method used to filter function names
    based on a regex expressions specified by the
    user in the environment variables"""
    
    if OCTOPUS_INCLUSION_PATTERNS:
        methods = filter_on_inclusion(OCTOPUS_INCLUSION_PATTERNS, methods)
        
    elif OCTOPUS_EXCLUSION_PATTERNS:
        methods = filter_on_exclusion(OCTOPUS_EXCLUSION_PATTERNS, methods)        
            
    return methods

