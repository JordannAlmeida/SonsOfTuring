import os
import logging
from typing import List, Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
BatchSpanProcessor,
ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

logger = logging.getLogger(os.getenv("APP_NAME", "OpenTelemetryConfig"))

class OpenTelemetryConfig:
    """
    Configuration class for OpenTelemetry SDK.
    Manages resource, tracer provider, exporters, and instrumentations.
    """

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "development",
        otlp_endpoint: Optional[str] = None,
        enable_console_exporter: bool = False,
        enable_fastapi_instrumentation: bool = True,
        enable_requests_instrumentation: bool = True,
        enable_logging_instrumentation: bool = True,
        enable_uvicorn_instrumentation: bool = True,
        additional_resource_attributes: Optional[dict] = None,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.otlp_endpoint = otlp_endpoint
        self.enable_console_exporter = enable_console_exporter
        self.enable_fastapi_instrumentation = enable_fastapi_instrumentation
        self.enable_requests_instrumentation = enable_requests_instrumentation
        self.enable_logging_instrumentation = enable_logging_instrumentation
        self.enable_uvicorn_instrumentation = enable_uvicorn_instrumentation
        self.additional_resource_attributes = additional_resource_attributes or {}

        self._resource: Optional[Resource] = None
        self._tracer_provider: Optional[TracerProvider] = None

    def _get_resource(self) -> Resource:
        """
        Creates and returns the OpenTelemetry Resource.
        """
        if self._resource:
            return self._resource

        default_attributes = {
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.environment,
        }
        all_attributes = {**default_attributes, **self.additional_resource_attributes}

        self._resource = Resource.create(all_attributes)
        return self._resource

    def _configure_tracer_provider(self):
        """
        Configures the global TracerProvider with appropriate span processors and exporters.
        """
        if self._tracer_provider:
            return

        resource = self._get_resource()
        self._tracer_provider = TracerProvider(resource=resource)

        # Configure OTLP Exporter
        if self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            self._tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(f"OpenTelemetry: OTLP Exporter enabled, sending to {self.otlp_endpoint}")
        else:
            logger.info("OpenTelemetry: OTLP Exporter disabled (no endpoint provided).")

        # Configure Console Exporter (for debugging)
        if self.enable_console_exporter:
            console_exporter = ConsoleSpanExporter()
            self._tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))
            logger.info("OpenTelemetry: Console Exporter enabled.")

        # Set the global tracer provider
        trace.set_tracer_provider(self._tracer_provider)
        logger.info("OpenTelemetry: Global TracerProvider configured.")

    def _instrument_libraries(self, app=None):
        """
        Applies automatic instrumentation to specified libraries.
        """
        if self.enable_fastapi_instrumentation:
            if app:
                FastAPIInstrumentor.instrument_app(app)
                logger.info("OpenTelemetry: FastAPI instrumentation enabled.")
            else:
                logger.warning("OpenTelemetry: FastAPI instrumentation requires 'app' argument, skipping.")

        if self.enable_requests_instrumentation:
            RequestsInstrumentor().instrument()
            logger.info("OpenTelemetry: Requests instrumentation enabled.")

        if self.enable_logging_instrumentation:

            LoggingInstrumentor().instrument(set_logging_format=False) # We manage format in core/logging.py
            logger.info("OpenTelemetry: Logging instrumentation enabled.")

    def initialize(self, app=None):
        """
        Initializes the OpenTelemetry SDK.
        Call this method once at the start of your application.
        """
        logger.info(f"Initializing OpenTelemetry for service: {self.service_name}...")
        self._configure_tracer_provider()
        self._instrument_libraries(app)
        logger.info("OpenTelemetry initialization complete.")

    def shutdown(self):
        """
        Shuts down the OpenTelemetry TracerProvider, flushing any pending spans.
        Call this before your application exits.
        """
        if self._tracer_provider:
            self._tracer_provider.shutdown()
            logger.info("OpenTelemetry: TracerProvider shut down.")