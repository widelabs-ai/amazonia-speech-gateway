from typing import Optional, Dict, Union
import io
import tiktoken
from pydub import AudioSegment
from openai import AsyncOpenAI
from openai._types import NotGiven, NOT_GIVEN
from .base import BaseAIModel


class GuaraModel(BaseAIModel):
    """Implementação do modelo Guará via API Guará usando biblioteca OpenAI"""
    
    SUPPORTED_MODELS = [
        "widelabs/guara-v2-2506"
    ]
    
    def __init__(self, base_url: str, token: str):
        super().__init__(base_url, token)
        self.client = AsyncOpenAI(
            api_key=token,
            base_url=base_url
        )
        
    async def transcribe(
        self,
        audio_content: bytes,
        model: str,
        language: str = "pt",
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Union[str, int]]:
        """Transcreve áudio usando o modelo Guará via API Guará com biblioteca OpenAI"""
        
        if not self.validate_model(model):
            raise ValueError(f"Modelo '{model}' não é suportado. Modelos disponíveis: {self.SUPPORTED_MODELS}")
        
        # Criar um objeto de arquivo em memória
        audio_file = io.BytesIO(audio_content)
        audio_file.name = "audio.wav"  # O OpenAI precisa de um nome de arquivo
        
        try:
            # Usar a biblioteca OpenAI para fazer a transcrição
            transcription = await self.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language=language,
                prompt=prompt if prompt else NOT_GIVEN,
                **kwargs  # Parâmetros adicionais
            )
            
            # Calcular tokens corretamente para o modelo Guará
            
            # INPUT TOKENS: 448 tokens a cada 30 segundos de áudio
            try:
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_content))
                audio_duration_seconds = len(audio_segment) / 1000.0 
                input_tokens = int((audio_duration_seconds / 30.0) * 448)
                
            except Exception as e:
                audio_size_kb = len(audio_content) / 1024
                input_tokens = max(1, int(audio_size_kb / 4))
            
            # OUTPUT TOKENS: Contar com tiktoken
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                output_tokens = len(encoding.encode(transcription.text))
                
            except Exception as e:
                output_tokens = max(1, int(len(transcription.text.split()) * 1.33))
            
            total_tokens = input_tokens + output_tokens
            
            result: Dict[str, Union[str, int]] = {
                "text": transcription.text,
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Erro na transcrição: {str(e)}")
    
    def get_supported_models(self) -> list[str]:
        """Retorna lista de modelos Guará suportados"""
        return self.SUPPORTED_MODELS.copy()
    
    def validate_model(self, model: str) -> bool:
        """Valida se o modelo Guará é suportado"""
        return model in self.SUPPORTED_MODELS
