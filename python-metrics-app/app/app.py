import os
from flask import Flask, Response
from prometheus_client import start_http_server, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Tracer setup
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "python-metrics-app"})
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name=os.environ.get("JAEGER_AGENT_HOST", "localhost"),
    agent_port=int(os.environ.get("JAEGER_AGENT_PORT", 6831)),

)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

REQUEST_COUNT = Counter('python_app_requests_total', 'Total app requests')
REQUEST_LATENCY = Histogram('python_app_request_latency_seconds', 'Request latency')

@app.route("/")
def index():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        time.sleep(random.uniform(0.1, 0.3))  # simulate latency
    return "Hello from Python App with metrics and tracing!"

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

