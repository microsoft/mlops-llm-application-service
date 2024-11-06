"""This module implements Open Telemetry configuration for the application."""

import logging

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)

from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider


class TelemetryConfigurator:
    """Configures the telemetry for the application."""

    def __init__(self, app_insights_connection_string):
        """Initialize the telemetry configurator."""
        self.app_insights_connection_string = app_insights_connection_string
        self.resource = Resource.create({ResourceAttributes.SERVICE_NAME: "sk_financial_analyst"})

    def set_up_logging(self):
        """Set Open Telemetry logging for the application."""
        exporter = AzureMonitorLogExporter(connection_string=self.app_insights_connection_string)

        # Create and set a global logger provider for the application.
        logger_provider = LoggerProvider(resource=self.resource)
        # Log processors are initialized with an exporter which is responsible
        # for sending the telemetry data to a particular backend.
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        # Sets the global default logger provider
        set_logger_provider(logger_provider)

        # Create a logging handler to write logging records, in OTLP format, to the exporter.
        handler = LoggingHandler()
        # Add filters to the handler to only process records from semantic_kernel.
        handler.addFilter(logging.Filter("semantic_kernel"))
        # Attach the handler to the root logger. `getLogger()` with no arguments returns the root logger.
        # Events from all child loggers will be processed by this handler.
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def set_up_tracing(self):
        """Set Open Telemetry tracing for the application."""
        exporter = AzureMonitorTraceExporter(connection_string=self.app_insights_connection_string)

        # Initialize a trace provider for the application. This is a factory for creating tracers.
        tracer_provider = TracerProvider(resource=self.resource)
        # Span processors are initialized with an exporter which is responsible
        # for sending the telemetry data to a particular backend.
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        # Sets the global default tracer provider
        set_tracer_provider(tracer_provider)

        # Get the tracer for the application.
        tracer = tracer_provider.get_tracer(__name__)
        return tracer

    def set_up_metrics(self):
        """Set Open Telemetry metrics for the application."""
        exporter = AzureMonitorMetricExporter(connection_string=self.app_insights_connection_string)

        # Initialize a metric provider for the application. This is a factory for creating meters.
        meter_provider = MeterProvider(
            metric_readers=[PeriodicExportingMetricReader(exporter, export_interval_millis=5000)],
            resource=self.resource,
            views=[
                # Dropping all instrument names except for those starting with "semantic_kernel"
                View(instrument_name="*", aggregation=DropAggregation()),
                View(instrument_name="semantic_kernel*"),
            ],
        )
        # Sets the global default meter provider
        set_meter_provider(meter_provider)
