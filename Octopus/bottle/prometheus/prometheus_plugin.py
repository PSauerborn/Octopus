"""Module containing prometheus plugin used to add
metrics route to an API"""

import logging 
import pydantic
import os
import typing

import bottle 

from Octopus.bottle.prometheus.prometheus_config import ENABLE_PROMETHEUS_METRICS, SERVICE_NAME, PROMETHEUS_MULTIPROC_DIR

LOGGER = logging.getLogger('octopus.prometheus.plugin')

if ENABLE_PROMETHEUS:
    LOGGER.info('applying prometheus metrics to application')
    
    from Octopus.bottle.prometheus import prometheus_metrics
    
    # create mappings used to map config settings to wrappers
    WRAPPER_MAPPINGS = {
        'latency': prometheus_metrics.prometheus_request_latency,
        'request_count': prometheus_metrics.prometheus_request_counter,
        'processing_requests': prometheus_metrics.IN_PROGRESS.track_inprogress()
    }
    
else:
    LOGGER.info('prometheus metrics are disabled. alter environment variables to enable')


class PrometheusConfig(pydantic.BaseModel):
    """Dataclass used to encapsulate the config settings
    used by the prometheus plugin"""
    
    metrics: typing.List[str]
    
class PrometheusPlugin:
    """Bottle Plugin classed used to add the 
    Prometheus Metric endpoints to an application"""
    
    _config = None
    
    def __init__(self, config: dict):
        
        try:
            self._config = PrometheusConfig(**config)
            
        except pydantic.ValidationError as err:
            LOGGER.exception(err)
            
            raise RuntimeError('received invalid config dict for prometheus plugin')
    
    def setup(self, app: bottle.Bottle):
        """
        Function called immediately after the
        apply() function has been called. The 
        setup function is used to ensure that the
        Promethes Metric plugin has not already been applied

        Arguments:
            app: instance of bottle.Bottle to apply plugin to
        """
        
        if not ENABLE_PROMETHEUS:
            return app
        
        for plugin in app.plugins:
            # if instance of Promethes Metric plugin has already been installed, raise exception
            if isinstance(plugin, PrometheusPlugin):
                raise RuntimeError('Instance of Promethes Metric Plugin Already Applied to Application')
        
        # add metrics route to application
        app.route('/metrics', callback=prometheus_metrics.get_prometheus_metrics)

    def apply(self, callback: object, context: bottle.Route):
        """
        Function used to wrap callback routes in
        Promethes Metric() decorator. The Promethes Metric decorator
        extracts spans from request headers (if present)
        and executes all further request in the context of
        said spans

        Arguments:
            callback: callback function for API route
            context: bottle.Route object giving Meta
                data about route and callback
        
        Returns:
            callback function wrapped in Promethes Metric decorator
        """
        
        if not ENABLE_PROMETHEUS:
            return callback
        
        for metric in self._config.metrics:
            wrapper = WRAPPER_MAPPINGS.get(metric, None)
            
            if wrapper is not None:
                LOGGER.debug('applying prometheus metric \'%s\'', metric)
                callback = wrapper(callback)
            else:
                LOGGER.warning('undefined metric mapping \'%s\'', metric)
        
        return callback

        
    
            
        