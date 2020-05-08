"""Module used to define config settings used by the octopus plugin"""

import logging 
import os

LOGGER = logging.getLogger('octopus.metrics.config')

ENABLE_JAEGER_TRACING = os.environ.get('ENABLE_JAEGER_TRACING', 'true') in ['true', 't']
ENABLE_PROMETHEUS_METRICS = os.environ.get('ENABLE_PROMETHEUS_METRICS', 'true').lower() in ['true', 't']

SERVICE_NAME = os.environ.get('SERVICE_NAME')