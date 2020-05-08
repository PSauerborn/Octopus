"""Module used to define config settings for the jaeger plugin"""

import os 
import logging 

LOGGER = logging.getLogger('octopus.jaeger.config')

SERVICE_NAME = os.environ.get('SERVICE_NAME')

JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))

ENABLE_JAEGER_TRACING = os.environ.get('ENABLE_JAEGER_TRACING', 'true') in ['true', 't']