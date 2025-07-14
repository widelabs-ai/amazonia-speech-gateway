# type: ignore
from dotenv import load_dotenv

load_dotenv()

import logging
import grpc
from concurrent import futures
import grpc_server.pb.speech_pb2 as speech_pb2
import grpc_server.pb.health_pb2 as health_pb2
from grpc_server.pb.speech_pb2_grpc import add_SpeechServiceServicer_to_server
from grpc_server.pb.health_pb2_grpc import add_HealthServiceServicer_to_server
from grpc_reflection.v1alpha import reflection
import asyncio
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorServer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from core.settings import settings
from grpc_server.services import SpeechService, HealthService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


trace.set_tracer_provider(
    TracerProvider(
        resource=Resource(
            attributes={
                "service.name": settings.otel_service_name,
            }
        )
    )
)

if settings.otel_exporter_otlp_endpoint is not None:
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )
else:
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )

grpc_client_instrumentor = GrpcAioInstrumentorServer()
grpc_client_instrumentor.instrument()


async def bootstrap() -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    add_SpeechServiceServicer_to_server(SpeechService(), server)
    add_HealthServiceServicer_to_server(HealthService(), server)

    SERVICE_NAMES = (
        health_pb2.DESCRIPTOR.services_by_name["HealthService"].full_name,
        speech_pb2.DESCRIPTOR.services_by_name["SpeechService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    port = "0.0.0.0:50051"
    server.add_insecure_port(port)
    await server.start()
    logger.info(f"AmazônIA - SPEECH GATEWAY gRPC: server listening on {port}")
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("Shutting down...")
        server.stop(None)
        await server.wait_for_termination()


def run() -> None:
    try:
        asyncio.run(bootstrap())
    except KeyboardInterrupt:
        logger.info("Received keyboardInterrupt, shutting down gracefully ...")
