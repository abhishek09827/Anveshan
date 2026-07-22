from fastapi import FastAPI
import uvicorn
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

res = Resource.create({"service.name": "anveshan-dev-lab"})
provider = TracerProvider(resource = res)
processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

trace.set_tracer_provider(provider)

app = FastAPI(title = "Anveshan Dev lab")

FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer("anveshan.manual.tracer")

@app.get("/")
def main():
    return {"mssg": "Anveshan Lab"}

@app.get("/manual-trace")
def manual_trace():
    with tracer.start_as_current_span("thinking_step") as span:
        span.set_attribute("agent.thought", "Deciding which tool to execute")
        span.set_attribute("agent.step_number", 1)
        with tracer.start_as_current_span("execute_tool") as tool_span:
            tool_span.set_attribute("tool.name", "calculator")
            tool_span.set_attribute("tool.input", "2 + 2")
            result = 4
            tool_span.set_attribute("tool.output", str(result))
    return {"status": "completed", "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)        