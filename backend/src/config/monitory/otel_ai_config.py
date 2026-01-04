import os
import logging
import base64

from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

logger = logging.getLogger(os.getenv("APP_NAME", "OpenTelemetryConfig"))

class OtelAIConfig:

    def initialize_langfuse(self):
        """
        Initializes Langfuse integration if API keys are provided.
        """
        LANGFUSE_AUTH = base64.b64encode(
            f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
        ).decode()
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
        trace_api.set_tracer_provider(tracer_provider=tracer_provider)

        AgnoInstrumentor().instrument()
        logger.info("Langfuse integration initialized.")

otel_ai_config = OtelAIConfig()