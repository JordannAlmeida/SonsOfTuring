import openlit
import os
import logging

logger = logging.getLogger(os.getenv("APP_NAME", "OpenTelemetryConfig"))

class OtelAIConfig:

    def initialize(self):
        """
        Initializes OpenTelemetry AI Exporter and instruments libraries if enabled.
        """
        openlit.init(
            application_name=os.getenv("APP_NAME", "SonsOfTuringAPI"),
            otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_AI_ENDPOINT"),
        )
        logger.info("OpenLIT initialization complete.")

otel_ai_config = OtelAIConfig()