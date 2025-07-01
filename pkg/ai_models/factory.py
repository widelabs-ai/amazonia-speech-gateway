from typing import Dict, Type


class ModelFactory:
    """Factory para criar instâncias de modelos de AI"""
    
    # Registro de modelos disponíveis
    _models: Dict[str, Type] = {}
    
    @classmethod
    def create_model(cls, provider: str, token: str):
        """
        Cria uma instância do modelo baseado no provider
        
        Args:
            provider: Nome do provider (guara, etc.)
            token: Token de autenticação
            
        Returns:
            BaseAIModel: Instância do modelo
            
        Raises:
            ValueError: Se o provider não for suportado
        """
        # Import tardio para evitar import circular
        from .guara import GuaraModel
        from core.settings import settings
        
        # Registrar modelos se ainda não estiverem registrados
        if not cls._models:
            cls._models = {
                "guara": GuaraModel,
                "guarapi": GuaraModel,  # Alias para guara
                "whisper": GuaraModel,  # Compatibility alias
            }
        
        provider_lower = provider.lower()
        
        if provider_lower not in cls._models:
            available = list(cls._models.keys())
            raise ValueError(f"Provider '{provider}' não suportado. Disponíveis: {available}")
        
        model_class = cls._models[provider_lower]
        return model_class(base_url=settings.guara_base_url, token=token)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Retorna lista de providers disponíveis"""
        # Import tardio para evitar import circular
        from .guara import GuaraModel
        
        # Registrar modelos se ainda não estiverem registrados
        if not cls._models:
            cls._models = {
                "guara": GuaraModel,
                "guarapi": GuaraModel,  # Alias para guara
                "whisper": GuaraModel,  # Compatibility alias
            }
        
        return list(cls._models.keys())
    
    @classmethod
    def register_model(cls, provider: str, model_class):
        """
        Registra um novo modelo no factory
        
        Args:
            provider: Nome do provider
            model_class: Classe do modelo
        """
        cls._models[provider.lower()] = model_class
