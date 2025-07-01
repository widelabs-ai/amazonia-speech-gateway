from grpc_server.pb.speech_pb2 import TranscriptionRequest
from core.use_cases.transcribe_audio.input import TranscribeAudioInput


def transcription_request_to_use_case_input(
    request: TranscriptionRequest,
) -> TranscribeAudioInput:
    return TranscribeAudioInput(
        audio_path=request.audio_path,
        token="",  # Token será obtido da configuração baseado no modelo
        model=request.model,
        prompt=request.prompt if request.prompt else None,
        language=request.language if request.language else "pt"
    )
