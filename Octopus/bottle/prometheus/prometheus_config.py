"""Module containing settings used for the Prometheus
bottle plugin"""

import logging 
import os
import pydantic
import typing

LOGGER = logging.getLogger('octopups.prometheus.config')

ENABLE_PROMETHEUS_METRICS = os.environ.get('ENABLE_PROMETHEUS_METRICS', 'true').lower() in ['true', 't']
PROMETHEUS_MULTIPROC_DIR = os.environ.get('prometheus_multiproc_dir', None)

SERVICE_NAME = os.environ.get('SERVICE_NAME')


class PrometheusConfig(pydantic.BaseModel):
    """Dataclass used to encapsulate the config settings
    used by the prometheus plugin"""
    
    metrics: typing.List[str] = ['latency', 'request_count', 'processing_requests']
    
PROMETHEUS_CONFIG = PrometheusConfig()