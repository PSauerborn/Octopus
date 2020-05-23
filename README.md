## Octopus - Distributed Tracing and Metric Library for Python

The Octopus Library for python introduces a series of distributed tracing 
applications designed to trace and monitor python micro-services via 
`Prometheus` and `Jaeger Tracing`. The majority of the codebase focuses
on plugins for python's `bottle` module, and features the following plugins
for any bottle application

#### `JaegerTracing`

Jaeger is a distributed tracing framework that implements the `opentracing` standard.
Incoming requests are traced and executed in the context of jaeger spans, which trace
requests and aggregates them on a jaeger backend. The plugin can be applied as follows

```python
import bottle

from Octopus.bottle.jaeger_tracing import tracing_plugin

app = bottle.Bottle()

if __name__ == '__main__':

    jaeger_config = {
        'jaeger_host': 'localhost',
        'jaeger_port': 6831,
        'service_name': 'demo-service'
    }

    app.install(tracing_plugin.JaegerTracing(jaeger_config=jaeger_config))

    app.run(host='localhost', port=10999)
```

The `JaegerTracing` plugin applies the `traced_request` wrapper to each route added
to the bottle application, which traces each request within a jaeger span and sends
the span to the specified jaeger agent (see https://www.jaegertracing.io/ for details
on Jaeger and its architecture). All traced requests can then be aggregated and viewed
on the jaeger backend.

Additionally, the `jaeger_tracing` library provides the `traced_requests` module, which
offers a library of HTTP request methods that inject jaeger spans into the header of the 
request, allowing spans and traces to be staggered across multiple micro-services. Note
that the `JaegerTracing` plugin automatically extracts any jaeger spans from the header
of incoming requests and uses said spans if present

#### `Prometheus`

Prometheus is a data aggregation/scraping service that collects and aggregates performance
metrics for applications. A Prometheus server is defined with a series of scrape jobs,
and each interval, the server will make a http request to the defined applications, gathers
the performance metrics and aggregates them on the server.

The `Prometheus` plugin adds the `/metrics` route needed by the Prometheus Server to the bottle
application. Additionally, the plugin wraps all routes on the application in a series of decorators
that measure request counts, request latency and in-progress requests. Performance metrics are 
stored on a local Prometheus Registry within the application until the Prometheus Server hits the
`/metrics` route to collect the stored metrics

```python
import bottle

from Octopus.bottle.prometheus import prometheus_plugin

app = bottle.Bottle()

if __name__ == '__main__':

    prometheus_config = {
        'service_name': 'demo-service',
        'metrics': ['latency', 'request_count', 'processing_requests']
    }

    app.install(prometheus_plugin.Prometheus(prometheus_config=prometheus_config))

    app.run(host='localhost', port=10999)
```

See https://prometheus.io/ for details on Prometheus and its configuration
