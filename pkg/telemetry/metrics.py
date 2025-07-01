from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from core.settings import settings

metric_reader = None

if settings.otel_exporter_otlp_endpoint is not None:
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
else:
    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())   
    
provider = MeterProvider(metric_readers=[metric_reader])

metrics.set_meter_provider(provider)

meter = metrics.get_meter("guardrails.meter")

resume_first_token_time = meter.create_histogram(
    name="resume_first_token_time",
    description="Tempo de resposta da emissão do primeiro token de resumo",
    unit="ms"
)

resume_time = meter.create_histogram(
    name="resume_time",
    description="Tempo total do resumo",
    unit="ms"
)

completion_first_token_time = meter.create_histogram(
    name="completion_first_token_time",
    description="Tempo de resposta da emissão do primeiro token",
    unit="ms"
)

completion_time = meter.create_histogram(
    name="completion_time",
    description="Tempo de resposta de uma compleção",
    unit="ms"
)