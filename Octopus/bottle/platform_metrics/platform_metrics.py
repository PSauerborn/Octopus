"""Platform Metrics plugin that combines prometheus metrics and jaeger tracing
in a single bottle plugin"""

import logging 
import os

import bottle

LOGGER = logging.getLogger('octopus.bottle.platform_metrics')

ENABLE_JAEGER_TRACING = os.environ.get('ENABLE_JAEGER_TRACING', 'false').lower() in ['true', 't']
ENABLE_PROMETHEUS_METRICS = os.environ.get('ENABLE_PROMETHEUS_METRICS', 'false').lower() in ['true', 't']
ENABLE_PLATFORM_METRICS = os.environ.get('ENABLE_PLATFORM_METRICS', 'false').lower() in ['true', 't']


class PlatformMetrics:
    """
    Bottle plugin for Platform Metrics, which utilizes both
    the Jaeger Tracing and Prometheus Metrics plugin to add
    distributed tracing to any bottle Application. Note that
    the Jaeger Tracing requires a working Jaeger Setup and the 
    Prometheus Metrics plugin requires a Prometheus Server to 
    scrape data
    
    Arguments:
        jaeger_config: dict containing jaeger_host, jaeger_port,
            service name and module name variables
        prometheus_config: dict containing service name and metrics list
    """
    
    def __init__(self, prometheus_config: dict = {}, jaeger_config: dict = {}):
        
        self._prometheus_config, self._jaeger_config = prometheus_config, jaeger_config
    
    def setup(self, app: bottle.Bottle):
        """
        Function called immediately after the
        apply() function has been called. The 
        setup function is used to ensure that the
        PlatformMetrics plugin has not already been applied
        and then applies both the JaegerTracing and Prometheus
        plugins

        Arguments:
            app: instance of bottle.Bottle to apply plugin to
        """
        
        if not ENABLE_PLATFORM_METRICS:
            LOGGER.info('platform metrics plugin is disabled')
            return
        
        LOGGER.info('applying platform metrics plugin')
        
        for plugin in app.plugins:
            # if instance of Tracing plugin has already been installed, raise exception
            if isinstance(plugin, PlatformMetrics):
                raise RuntimeError('instance of platform metrics plugin already applied to application')
        
        if ENABLE_JAEGER_TRACING:
            from Octopus.bottle.jaeger_tracing import tracing_plugin
            
            LOGGER.info('adding Jaeger Tracing plugin to bottle application')
            app.install(tracing_plugin.JaegerTracing(self._jaeger_config))
            
        if ENABLE_PROMETHEUS_METRICS:
            from Octopus.bottle.prometheus import prometheus_plugin
            
            LOGGER.info('adding Prometheus Metric plugin to bottle application')
            app.install(prometheus_plugin.Prometheus(self._prometheus_config))
            
    def apply(self, callback: object, context: bottle.Route):
        """Function used to wrap callbacks. Note that the 
        callback wrapping is handled by the JaegerTracing
        and Prometheus plugins, not the PlatformMetrics
        plugin
        
        Arguments:
            callback: callback function for API route
            context: bottle.Route object giving Meta
                data about route and callback
        
        Returns:
            callback function wrapped in tracing decorator
        """
        
        return callback