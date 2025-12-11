# app/utils/aes_gcm_utils.py
import os
import json
import base64
from typing import Any, Optional, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _b64(x: bytes) -> str:
    return base64.b64encode(x).decode()

def _unb64(s: Optional[str]) -> Optional[bytes]:
    return base64.b64decode(s) if s is not None else None

def encrypt_json(key: bytes, obj: Any, aad: Optional[bytes] = None) -> Dict[str, Optional[str]]:
    """
    Returns {"data": base64(nonce + ciphertext+tag), "aad": base64(aad) or None}
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    plaintext = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
    combined = nonce + ciphertext
    return {"data": _b64(combined), "aad": _b64(aad) if aad else None}

def decrypt_json(key: bytes, data_b64: str, aad_b64: Optional[str] = None) -> Any:
    """
    Accepts base64(nonce + ciphertext+tag) and optional base64 aad.
    Returns python object (decoded JSON) or raises ValueError.
    """
    try:
        combined = base64.b64decode(data_b64)
        if len(combined) < 13:
            raise ValueError("ciphertext too short")
        nonce = combined[:12]
        ciphertext = combined[12:]
        aad = _unb64(aad_b64) if aad_b64 else None
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
        return json.loads(plaintext.decode("utf-8"))
    except Exception as e:
        raise ValueError("decryption failed") from e
