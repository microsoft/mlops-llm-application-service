# https://github.com/Azure-Samples/app-service-sidecar-tutorial-prereqs/blob/main/images/otel-collector/otel-collector-config.yaml

FROM otel/opentelemetry-collector-contrib:0.91.0

COPY otel-collector-config.yaml /etc/otelcol-contrib/config.yaml

ENTRYPOINT ["/otelcol-contrib"]

CMD ["--config", "/etc/otelcol-contrib/config.yaml"]
EXPOSE 4317 55679 4318
