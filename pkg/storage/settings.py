from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    key_id: str = Field(alias="ORACLE_S3_ACCESS_KEY_ID")
    key_secret: str = Field(alias="ORACLE_S3_SECRET")
    bucket: str = Field(alias="ORACLE_S3_BUCKET")
    bucket_endpoint: str = Field(alias="ORACLE_S3_ENDPOINT")
    bucket_region: str = Field(alias="ORACLE_S3_REGION")


settings = Settings()  # type: ignore
