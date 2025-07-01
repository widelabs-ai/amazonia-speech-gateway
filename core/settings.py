from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Configurações para o modelo Guará
    guara_base_url: str = Field(alias="GUARA_BASE_URL", default="http://164.152.56.41:81/v1")
    
    # Token específico para o modelo widelabs/guara-v2-2506
    guarav2_2506_token: Optional[str] = Field(alias="GUARAV2_2506_TOKEN", default=None)
    
    # Configurações de telemetria (todas opcionais)
    otel_exporter_otlp_endpoint: Optional[str] = Field(alias="OTEL_EXPORTER_OTLP_ENDPOINT", default=None)
    otel_service_name: Optional[str] = Field(alias="OTEL_SERVICE_NAME", default="amazonia-speech-gateway")
    otel_sdk_disabled: bool = Field(alias="OTEL_SDK_DISABLED", default=False)
    
    # Configurações do Oracle Object Storage (opcionais)
    oracle_config_file_path: Optional[str] = Field(alias="ORACLE_CONFIG_FILE_PATH", default=None)
    oracle_profile_name: Optional[str] = Field(alias="ORACLE_PROFILE_NAME", default="DEFAULT")


settings = Settings() # type: ignore