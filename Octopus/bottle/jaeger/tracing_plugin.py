"""Module containing the API Tracing plugin. Plugins can
be installed using the bottle.install() method. The plugin
implements the OpenTracing standard via the Jaeger Tracing
framework"""


import bottle

from Octopus.bottle.jaeger import tracing
from Octopus.bottle.jaeger.jaeger_config import ENABLE_JAEGER_TRACING


class JaegerTracing:
    """Bottle plugin for API Tracing. All tracing is done via the 
    opentracing standard with a Backend Jaeger Service to 
    collect and aggregate the traces. Note that
    the Tracing Plugin should be applied last to ensure
    that all routes that have been added by other plugins
    are traced
    
    Arguments:
        jaeger_config: dict containing jaeger_host, jaeger_port,
            service name and module name variables
    """
    
    def __init__(self, jaeger_config: dict = None):
        
        pass
    
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
            if isinstance(plugin, JaegerTracing):
                raise RuntimeError('Instance of Tracing Plugin Already Applied to Application')

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

        route_name = context['rule']
        
        return tracing.trace(route_name)(callback) if ENABLE_JAEGER_TRACING else callback
