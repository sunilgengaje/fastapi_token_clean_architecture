# app/client_secure.py
import os, base64, json, requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key_b64 = os.environ.get("AESGCM_KEY") or os.environ.get("AES_KEY_B64")
if not key_b64:
    raise SystemExit("Set AESGCM_KEY in .env or AES_KEY_B64 in environment")
KEY = base64.b64decode(key_b64)
AES = AESGCM(KEY)
BASE = "http://127.0.0.1:8000"  # change port if you started uvicorn on other port

def encrypt(obj):
    import os, json, base64
    nonce = os.urandom(12)
    pt = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ct = AES.encrypt(nonce, pt, None)
    return {"data": base64.b64encode(nonce + ct).decode(), "aad": None}

def decrypt(blob):
    import base64, json
    combined = base64.b64decode(blob["data"])
    nonce, ct = combined[:12], combined[12:]
    pt = AES.decrypt(nonce, ct, None)
    return json.loads(pt.decode("utf-8"))

# Example: encrypted register
payload = {
  "username": "secureuser",
  "email": "secure@example.com",
  "full_name": "Secure User",
  "password": "secret123"
}
blob = encrypt(payload)
resp = requests.post(f"{BASE}/secure/auth/register", json=blob)
print("status:", resp.status_code)
print("raw text:", resp.text)
resp.raise_for_status()
resp_blob = resp.json()
print("Encrypted response:", resp_blob)
plain = decrypt(resp_blob)
print("Decrypted response:", json.dumps(plain, indent=2, ensure_ascii=False))
