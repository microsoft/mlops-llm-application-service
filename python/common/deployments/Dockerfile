# Use an official Python runtime as a parent image
FROM python:3.12.7-slim-bullseye AS builder

CMD ["python", "-c", "import os; print(os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT'))"]

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app/requirements.txt
COPY requirements.txt  /app/requirements.txt

# Install any needed packages specified in requirements.txt
# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Verify that site-packages exists (optional)
RUN ls /usr/local/lib/python3.12/site-packages

# Stage 2: Production
FROM python:3.12.7-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH="/app"

ARG OTEL_COLLECTOR_HOST \
    OTEL_COLLECTOR_PORT_GRPC \
    OTEL_COLLECTOR_PORT_HTTP \
    OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED \
    NEWS_ANALYST_MODEL_NAME\
    FINANCIAL_ANALYST_MODEL_NAME \
    REPORT_GENERATOR_MODEL_NAME \
    KEY_VAULT_URL \
    OTEL_SERVICE_NAME \
    OTEL_LOGS_EXPORTER \
    OTEL_TRACES_EXPORTER \
    OTEL_EXPORTER_OTLP_PROTOCOL \
    OTEL_EXPORTER_OTLP_INSECURE \
    OTEL_LOG_LEVEL \
    OTEL_RESOURCE_ATTRIBUTES \
    AZURE_CLIENT_ID \
    AZURE_TENANT_ID \
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT \
    OTEL_EXPORTER_OTLP_ENDPOINT


# Install runtime dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser

# Set work directory
WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy installed executables from builder
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the entire application code
COPY common/configurator/ /app/common/configurator/
COPY sk_financial_analyst/config/ /app/sk_financial_analyst/config/
COPY sk_financial_analyst/executors/ /app/sk_financial_analyst/executors/
COPY sk_financial_analyst/llm_application/ /app/sk_financial_analyst/llm_application/
COPY sk_financial_analyst/llm_application/assistants/ /app/sk_financial_analyst/llm_application/assistants/
COPY sk_financial_analyst/llm_application/plugins/ /app/sk_financial_analyst/llm_application/plugins/
COPY sk_financial_analyst/utils/ /app/sk_financial_analyst/utils/
COPY sk_financial_analyst/routes/ /app/sk_financial_analyst/routes/

# Change ownership of the /app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 8000 for the FastAPI application
EXPOSE 8000

CMD ["uvicorn", "sk_financial_analyst.routes.routes:app", "--port", "8000", "--host", "0.0.0.0"]
