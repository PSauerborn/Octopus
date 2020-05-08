"""Module containing settings used for the Prometheus
bottle plugin"""

import logging 
import os

LOGGER = logging.getLogger('octopups.prometheus.config')


ENABLE_PROMETHEUS_METRICS = os.environ.get('ENABLE_PROMETHEUS_METRICS', 'true').lower() in ['true', 't']
PROMETHEUS_MULTIPROC_DIR = os.environ.get('prometheus_multiproc_dir', None)

SERVICE_NAME = os.environ.get('SERVICE_NAME')