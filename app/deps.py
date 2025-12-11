# app/deps.py
import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_aes_key() -> bytes:
    """
    Prefer AESGCM_KEY (from .env). Backwards compatible with AES_KEY_B64.
    Returns raw bytes (32 bytes expected).
    """
    key_b64 = os.environ.get("AESGCM_KEY") or os.environ.get("AES_KEY_B64")
    if key_b64:
        try:
            key = base64.b64decode(key_b64)
            if len(key) != 32:
                raise ValueError("AES key must be 32 bytes (base64 of 32 bytes)")
            return key
        except Exception as e:
            raise RuntimeError(f"Invalid AES key in environment: {e}")
    # development fallback (only for dev)
    return AESGCM.generate_key(bit_length=256)
