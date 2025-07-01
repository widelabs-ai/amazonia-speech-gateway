import grpc  # type: ignore
from grpc_server.pb.health_pb2_grpc import HealthServiceServicer  # type: ignore
from grpc_server.pb.health_pb2 import HealthResponse, Blank  # type: ignore


class HealthService(HealthServiceServicer):  # type: ignore
    async def isOk(
        self, request: Blank, context: grpc.ServicerContext
    ) -> HealthResponse:
        return HealthResponse(code=0)
