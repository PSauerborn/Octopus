"""Module defining a series of exceptions that are raised
by the prometheus module"""

import logging

LOGGER = logging.getLogger('octopus.bottle.prometheus')


class PrometheusConfigurationException(BaseException):
    """Exception raised when an invalid configuration
    is passed to the prometheus plugin"""