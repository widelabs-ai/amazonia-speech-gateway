from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
import asyncio


class BaseAIModel(ABC):
    """Classe base abstrata para modelos de AI"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
    
    @abstractmethod
    async def transcribe(
        self,
        audio_content: bytes,
        model: str,
        language: str = "pt",
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Union[str, int]]:
        """
        Método abstrato para transcrição de áudio
        
        Args:
            audio_content: Conteúdo do arquivo de áudio em bytes
            model: Nome do modelo a ser usado
            language: Idioma do áudio
            prompt: Prompt opcional para guiar a transcrição
            **kwargs: Parâmetros adicionais específicos do modelo
            
        Returns:
            Dict[str, Union[str, int]]: Dicionário contendo:
                - text: Texto transcrito
                - prompt_tokens: Tokens de entrada
                - completion_tokens: Tokens de saída
                - total_tokens: Total de tokens
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> list[str]:
        """
        Retorna lista de modelos suportados
        
        Returns:
            list[str]: Lista de nomes dos modelos
        """
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """
        Valida se o modelo é suportado
        
        Args:
            model: Nome do modelo
            
        Returns:
            bool: True se suportado, False caso contrário
        """
        pass
