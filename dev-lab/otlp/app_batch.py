from fastapi import FastAPI
import uvicorn
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

res = Resource.create({"service.name": "anveshan-dev-lab"})
provider = TracerProvider(resource = res)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

trace.set_tracer_provider(provider)

app = FastAPI(title = "Anveshan Dev lab")

FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer("anveshan.manual.tracer")

@app.get("/")
def main():
    return {"mssg": "Anveshan Lab"}

@app.get("/otlp-trace")
def otlp_test():
    with tracer.start_as_current_span("otlp_parent_span") as span:
        span.set_attribute("experiment", "module_2_otlp")
        with tracer.start_as_current_span("otlp_child_span"):
            return {"status": "OTLP span created!"}

    return {"status": "completed", "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)        