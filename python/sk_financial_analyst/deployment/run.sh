#!/usr/bin/env bash

OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-"promptflow.dag.fastapi"}"
OTEL_SERVICE_VERSION="${OTEL_SERVICE_VERSION:-"0.0.0"}"
uuid=$(python -c "import uuid; print(uuid.uuid4())")
OTEL_SERVICE_INSTANCE_ID=${OTEL_SERVICE_INSTANCE_ID:-${uuid}}


export OTEL_RESOURCE_ATTRIBUTES="service.version=${OTEL_SERVICE_VERSION},service.instance.id=${OTEL_SERVICE_INSTANCE_ID}"

export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --service_name "${OTEL_SERVICE_NAME}"  \
    --exporter_otlp_endpoint  "${OTEL_EXPORTER_OTLP_ENDPOINT}" \
    python -m sk_financial_analyst.executors.single_item_executor MSFT .data/outputs
