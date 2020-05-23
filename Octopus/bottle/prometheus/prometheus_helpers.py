"""Module containing a series of helper functions used by the
prometheus server metrics module"""

import logging 

import Octopus.bottle.prometheus.prometheus_config as config


LOGGER = logging.getLogger('octopus.bottle.prometheus')

def parse_auth_token(token: str) -> str:
    """Helper function used to parse authentication
    token sent by prometheus server from /metrics route"""
    
    if not token.startswith('Bearer '):
        return None
    
    return token.split('Bearer ')[1]
    
def is_authenticated_user(token: str) -> bool:
    """Helper function used to determine if a 
    user has access to the /metrics route"""
    
    return config.PROMETHEUS_CONFIG.prometheus_auth_token == parse_auth_token(token)