from pydantic import BaseModel
from typing import Optional


class TranscribeAudioInput(BaseModel):
    audio_path: str
    token: str
    model: str
    prompt: Optional[str] = None
    language: str = "pt"
