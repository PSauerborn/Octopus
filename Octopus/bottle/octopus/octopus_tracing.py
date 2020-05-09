"""Octopus plugin that combines prometheus metrics and jaeger tracing
in a single bottle plugin"""

import logging 

import bottle

from Octopus.bottle.octopus.octopus_config import ENABLE_PROMETHEUS_METRICS, ENABLE_JAEGER_TRACING

LOGGER = logging.getLogger('octopus.metrics.plugin')


class OctopusDeepMetricPlugin:
    """
    Bottle plugin for the Octopus Plugin, which utilized both
    the Jaeger Tracing and Prometheus Metrics plugin to add
    distributed tracing to any bottle Application. Note that
    the Jaeger Tracing requires a working Jaeger Setup and the 
    Prometheus Metrics plugin requires a Prometheus Server to 
    scrape data
    
    Arguments:
        jaeger_config: dict containing jaeger_host, jaeger_port,
            service name and module name variables
    """
    
    def __init__(self, prometheus_config: dict = {}, jaeger_config: dict = {}):
        
        self._prometheus_config, self._jaeger_config = prometheus_config, jaeger_config
    
    def setup(self, app: bottle.Bottle):
        """
        Function called immediately after the
        apply() function has been called. The 
        setup function is used to ensure that the
        Tracing plugin has not already been applied

        Arguments:
            app: instance of bottle.Bottle to apply plugin to
        """
        
        for plugin in app.plugins:
            # if instance of Tracing plugin has already been installed, raise exception
            if isinstance(plugin, OctopusDeepMetricPlugin):
                raise RuntimeError('Instance of Octopus Tracing Plugin Already Applied to Application')
            
        if ENABLE_PROMETHEUS_METRICS:
            from Octopus.bottle.prometheus import prometheus_plugin
            
            LOGGER.info('adding Prometheus Metric plugin to bottle application')
            
            app.install(prometheus_plugin.PrometheusPlugin(self._prometheus_config))
        
        if ENABLE_JAEGER_TRACING:
            from Octopus.bottle.jaeger import tracing_plugin
            
            LOGGER.info('adding Jaeger Tracing plugin to bottle application')
            
            app.install(tracing_plugin.JaegerTracing(self._jaeger_config))
            
    def apply(self, callback: object, context: bottle.Route):
        """
        Function used to wrap callback routes in
        tracing() decorator. The tracing decorator
        extracts spans from request headers (if present)
        and executes all further request in the context of
        said spans

        Arguments:
            callback: callback function for API route
            context: bottle.Route object giving Meta
                data about route and callback
        
        Returns:
            callback function wrapped in tracing decorator
        """
        
        return callback