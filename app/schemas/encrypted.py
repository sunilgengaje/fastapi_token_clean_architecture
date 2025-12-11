# app/schemas/encrypted.py
from pydantic import BaseModel
from typing import Optional

class EncryptedBlob(BaseModel):
    data: str
    aad: Optional[str] = None
