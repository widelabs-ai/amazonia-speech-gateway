import grpc
from grpc_server.pb.speech_pb2_grpc import SpeechServiceServicer
from grpc_server.pb.speech_pb2 import TranscriptionRequest, TranscriptionResponse
from core.use_cases.transcribe_audio.handler import execute as transcribe_audio
from grpc_server.hydrators.transcription_request_to_use_case_input import (
    transcription_request_to_use_case_input
)
from pkg.ai_models import ModelFactory
from pydantic import ValidationError
from pkg.telemetry import tracer


class SpeechService(SpeechServiceServicer):
    async def transcribe(
        self, 
        request: TranscriptionRequest, 
        context: grpc.ServicerContext
    ) -> TranscriptionResponse:
        try:
            with tracer.start_as_current_span("grpc_transcribe_request"):
                # Validar campos obrigatórios
                if not request.audio_path:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("audio_path é obrigatório")
                    return TranscriptionResponse()
                
                if not request.model:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("model é obrigatório")
                    return TranscriptionResponse()
                
                # Validar se o modelo é suportado
                try:
                    # Usar um token temporário apenas para validação do modelo
                    temp_model_instance = ModelFactory.create_model("guara", "temp_token")
                    if not temp_model_instance.validate_model(request.model):
                        supported_models = temp_model_instance.get_supported_models()
                        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                        context.set_details(f"Modelo '{request.model}' não suportado. Modelos disponíveis: {supported_models}")
                        return TranscriptionResponse()
                except ValueError as e:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(f"Erro ao validar modelo: {str(e)}")
                    return TranscriptionResponse()
                
                # Converter request para input do caso de uso
                input_data = transcription_request_to_use_case_input(request)
                
                # Executar transcrição
                result = await transcribe_audio(input_data)
                
                response = TranscriptionResponse(
                    text=result.text,
                    duration=result.duration,
                    prompt_tokens=result.prompt_tokens,
                    completion_tokens=result.completion_tokens,
                    total_tokens=result.total_tokens
                )
                
                return response
                
        except ValidationError as e:
            print(f"Validation error: {e.errors()}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid request: {e}")
            return TranscriptionResponse()
        except FileNotFoundError as e:
            print(f"Audio file not found: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Audio file not found")
            return TranscriptionResponse()
        except Exception as e:
            print(f"Transcription error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal transcription error")
            return TranscriptionResponse()
