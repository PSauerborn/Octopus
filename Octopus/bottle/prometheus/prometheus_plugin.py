"""Module containing prometheus plugin used to add
metrics route to an API"""

import logging 
import pydantic
import os
import typing

import bottle 

import Octopus.bottle.prometheus.prometheus_config as config


LOGGER = logging.getLogger('octopus.bottle.prometheus')

# import prometheus metrics module if enabled. Note that this should be done dynamically to avoid creating the
# prometheus registry if the plugin is not enabled
if config.ENABLE_PROMETHEUS_METRICS:
    LOGGER.info('applying prometheus metrics to application')
    
    from Octopus.bottle.prometheus import prometheus_metrics
    
    # create mappings used to map config settings to wrappers
    WRAPPER_MAPPINGS = {
        'latency': prometheus_metrics.prometheus_request_latency,
        'request_count': prometheus_metrics.prometheus_request_counter,
        'processing_requests': prometheus_metrics.prometheus_in_progress_requests
    }
    
else:
    LOGGER.info('prometheus metrics are disabled. alter environment variables to enable')

    
class Prometheus:
    """Bottle Plugin classed used to add the 
    Prometheus Metric endpoints to an application.
    The plugin exposes the /metrics route for the 
    Prometheus server to scrape metrics from. It also
    decorates the application routes with a collection
    of metric decorators to measure various performance
    metrics"""
    
    def __init__(self, prometheus_config: dict = {}):
        
        config.set_prometheus_config(prometheus_config)
    
    def setup(self, app: bottle.Bottle):
        """
        Function called immediately after the
        apply() function has been called. The 
        setup function is used to ensure that the
        Promethes Metric plugin has not already been applied
        and adds the /metrics route

        Arguments:
            app: instance of bottle.Bottle to apply plugin to
        """
        
        if not config.ENABLE_PROMETHEUS_METRICS:
            return app
        
        for plugin in app.plugins:
            # if instance of Promethes Metric plugin has already been installed, raise exception
            if isinstance(plugin, Prometheus):
                raise RuntimeError('Instance of Promethes Metric Plugin Already Applied to Application')
        
        # add metrics route to application
        app.route('/metrics', callback=prometheus_metrics.get_prometheus_metrics)

    def apply(self, callback: object, context: bottle.Route):
        """
        Function used to wrap callback routes in
        various prometheus metric decorator(s). The 
        decorators gather various performance metrics
        which are stored in the global registry for the
        prometheus server to scrape

        Arguments:
            callback: callback function for API route
            context: bottle.Route object giving Meta
                data about route and callback
        
        Returns:
            callback function wrapped in Promethes Metric decorator
        """
        
        if not config.ENABLE_PROMETHEUS_METRICS:
            return callback
        
        for metric in config.PROMETHEUS_CONFIG.metrics:
            wrapper = WRAPPER_MAPPINGS.get(metric, None)
            
            if wrapper is not None:
                LOGGER.debug('applying prometheus metric \'%s\'', metric)
                callback = wrapper(callback)
            else:
                LOGGER.warning('undefined metric mapping \'%s\'', metric)
        
        return callback

        
    
            
        