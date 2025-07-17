from .input import TranscribeAudioInput
from pkg.storage import client as storage_client
from pkg.ai_models import ModelFactory
from pkg.telemetry import tracer
from core.utils import MsCounter
from core.settings import settings
import asyncio
import logging

# Configurar logger
logger = logging.getLogger(__name__)


def get_token_for_model(model: str) -> str:
    """
    Retorna o token apropriado baseado no modelo solicitado
    
    Args:
        model: Nome do modelo (ex: "widelabs/guara-v2-2506")
        
    Returns:
        str: Token configurado para o modelo
        
    Raises:
        ValueError: Se o token não estiver configurado para o modelo
    """
    # Mapear modelos para tokens específicos
    model_token_mapping = {
        "widelabs/guara-v2-2506": settings.guarav2_2506_token
    }
    
    # Verificar se há token específico para o modelo
    token = model_token_mapping.get(model)
    
    if token:
        return token
    
    raise ValueError(f"Token não configurado para o modelo '{model}'. Configure GUARAV2_2506_TOKEN nas variáveis de ambiente.")


class TranscriptionResult:
    def __init__(self, text: str, duration: float, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0):
        self.text = text
        self.duration = duration
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


async def execute(input_data: TranscribeAudioInput) -> TranscriptionResult:
    """Executa a transcrição de áudio"""
    
    with tracer.start_as_current_span("transcribe_audio") as span:
        counter = MsCounter()
        
        span.set_attributes({
            "audio_path": input_data.audio_path,
            "model": input_data.model,
            "language": input_data.language,
            "has_prompt": input_data.prompt is not None,
            "has_token": bool(input_data.token)
        })
        
        try:
            logger.info(f"Starting transcription for audio_path: {input_data.audio_path}, model: {input_data.model}")
            
            # Verificar se é um arquivo local ou caminho do Object Storage
            # Arquivos locais começam com '/' ou '.' ou 'C:' (Windows)
            # Arquivos do Oracle Storage são paths simples como "temp-audio/uuid.wav"
            if (input_data.audio_path.startswith('/') or 
                input_data.audio_path.startswith('./') or 
                input_data.audio_path.startswith('../') or
                ':' in input_data.audio_path[:3]):  # Windows C: D: etc
                # Arquivo local - ler diretamente
                span.add_event("reading_local_audio_file")
                logger.info(f"Reading local audio file: {input_data.audio_path}")
                try:
                    with open(input_data.audio_path, 'rb') as f:
                        audio_content = f.read()
                    logger.info(f"Successfully read local file, size: {len(audio_content)} bytes")
                except Exception as e:
                    logger.error(f"Failed to read local file {input_data.audio_path}: {str(e)}")
                    raise FileNotFoundError(f"Cannot read local file: {str(e)}")
            else:
                # Arquivo no Object Storage - baixar usando o storage client
                span.add_event("downloading_audio_from_oracle_storage")
                logger.info(f"Downloading audio from Oracle Storage: {input_data.audio_path}")
                try:
                    audio_content = storage_client.get_bytes(input_data.audio_path)
                    logger.info(f"Successfully downloaded from Oracle Storage, size: {len(audio_content)} bytes")
                except Exception as e:
                    logger.error(f"Failed to download from Oracle Storage {input_data.audio_path}: {str(e)}")
                    raise FileNotFoundError(f"Cannot download from Oracle Storage: {str(e)}")
            
            # Criar instância do modelo baseado no provider
            # Usar "guara" como provider padrão para o modelo Guará
            span.add_event("creating_model_instance")
            logger.info(f"Creating model instance for model: {input_data.model}")
            
            # Obter o token apropriado para o modelo
            try:
                model_token = get_token_for_model(input_data.model)
                logger.info(f"Token obtained for model: {input_data.model}")
            except ValueError as e:
                logger.error(f"Token configuration error for model {input_data.model}: {str(e)}")
                raise ValueError(str(e))
            
            try:
                model_instance = ModelFactory.create_model("guara", model_token)
                logger.info("Model instance created successfully")
            except Exception as e:
                logger.error(f"Failed to create model instance: {str(e)}")
                raise Exception(f"Model creation failed: {str(e)}")
            
            # Transcrever o áudio
            span.add_event("starting_transcription")
            logger.info("Starting audio transcription")
            try:
                transcription_response = await model_instance.transcribe(
                    audio_content=audio_content,
                    model=input_data.model,
                    language=input_data.language,
                    prompt=input_data.prompt
                )
                logger.info("Transcription completed successfully")
            except Exception as e:
                logger.error(f"Transcription failed: {str(e)}")
                raise Exception(f"Transcription error: {str(e)}")
            
            duration = counter.snapshot()
            span.add_event("transcription_completed", attributes={"duration_ms": duration})
            
            logger.info(f"Transcription process completed in {duration}ms")
            
            # Agora transcription_response é um dicionário com texto e tokens
            return TranscriptionResult(
                text=transcription_response["text"],
                duration=duration,
                prompt_tokens=transcription_response["prompt_tokens"],
                completion_tokens=transcription_response["completion_tokens"],
                total_tokens=transcription_response["total_tokens"]
            )
            
        except Exception as e:
            logger.error(f"Error in transcribe_audio execution: {str(e)}", exc_info=True)
            span.record_exception(e)
            raise e
