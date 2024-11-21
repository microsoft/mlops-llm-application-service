# Use an official Python runtime as a parent image
FROM python:3.12.7-slim-bullseye AS builder

CMD ["python", "-c", "import os; print(os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT'))"]

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
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
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m appuser

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

# Change ownership of the /app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Define environment variables for Uvicorn (optional)
ENV PORT=8000

ENV PYTHONPATH="/app"

CMD ["uvicorn", "sk_financial_analyst.routes.routes:app", "--port", "8000", "--host", "0.0.0.0"]
