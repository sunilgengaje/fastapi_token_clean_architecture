<!-- .github/copilot-instructions.md -->
# Copilot / AI assistant guide — fastapi_token_clean_architecture

Purpose: short, actionable rules and examples so an AI coding assistant becomes productive immediately in this repo.

- **Big picture**: This is a small FastAPI app organized with a clean-architecture style:
  - **API layer**: `app/routers/*` (APIRouter endpoints)
  - **Domain services**: `app/services/*` (business rules, e.g. `AuthService`)
  - **Persistence**: `app/repositories/*` and `app/models/*` (SQLAlchemy)
  - **Schemas**: `app/schemas/*` (Pydantic v2 models)
  - **Cross-cutting**: `app/middleware/*`, `app/utils/*` (encryption, JWT, logging)
  - **Entrypoint**: `app/main.py` (dev-only DB create, middleware registration, router includes)

- **Key files to read first**: `app/main.py`, `app/config.py`, `app/middleware/aes_gcm_middleware.py`,
  `app/middleware/logging_middleware.py`, `app/routers/auth_router.py`, `app/services/auth_service.py`,
  `app/utils/aes_gcm_utils.py`, `app/client_example.py`, `requirements.txt`.

- **Auth & session flow (concise)**:
  - `POST /auth/register` and `POST /auth/login` are implemented in `app/routers/auth_router.py`.
  - `AuthService` (in `app/services/auth_service.py`) uses `UserRepository` to CRUD users and `app.utils.jwt_utils` to create/validate tokens.
  - Sessions are created with `create_session` (see `app/services/session_service.py`) and stored in `UserSession` model; session id is returned as a cookie `session_id`.

- **Encryption flow (project-specific)**:
  - AES-GCM utilities: `app/utils/aes_gcm_utils.py`. `encrypt_bytes` / `decrypt_bytes` exchange base64(nonce || ciphertext_with_tag).
  - Middleware: `app/middleware/aes_gcm_middleware.py` — when the request header `X-Encrypted: 1` is present the middleware expects the body to be `application/octet-stream` containing base64 blob, decrypts it and replaces the request body for downstream handlers; responses are encrypted back and returned as base64 blob with header `x-encrypted: 1`.
  - AES key: controlled by env var `AESGCM_KEY` (base64). If missing, a dev key is auto-generated (printed warning) — do NOT rely on this in production. See `app/config.py`.
  - Example client: `app/client_example.py` shows how to call `http://127.0.0.1:8000/enc/auth/register` with `X-Encrypted: 1` and `Content-Type: application/octet-stream`.

- **Logging**:
  - `app/middleware/logging_middleware.py` writes `AccessLog` rows and per-session files (`logs/sessions/`).
  - `app/main.py` registers the logging middleware before routers — middleware ordering is meaningful; preserve ordering when adding middleware.

- **Developer workflows & commands (verified in repo)**:
  - Run dev server:
    - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
  - Run the example encrypted client:
    - `PYTHONPATH=. python -m app.client_example` or `PYTHONPATH=. python app/client_example.py`
  - Quick encrypt/decrypt test (python REPL snippet):
    - `PYTHONPATH=. python - <<'PY'\nfrom app.utils.aes_gcm_utils import encrypt_bytes, decrypt_bytes\nprint(encrypt_bytes(b'...'))\nPY`
  - If you receive an encrypted server response in `resp.enc`, decrypt locally using `app.utils.aes_gcm_utils.decrypt_bytes` (see `app/client_example.py` for pattern).

- **Project-specific patterns / conventions**:
  - Pydantic v2 settings: `app/config.py` exports `settings = Settings()` and reads from `.env`.
  - The project uses SQLAlchemy ORM models plus a simple `Base.metadata.create_all(bind=engine)` in `app/main.py` (dev convenience). In production, use Alembic migrations.
  - Services accept FastAPI DI `Depends()` for DB session injection (see `AuthService.__init__`). Keep that pattern when adding new services.
  - Repositories are thin wrappers around SQLAlchemy queries — avoid changing model fields lightly.

- **What to change (editing guidance)**:
  - When adding middleware that needs to modify request bodies (like AES decryption), register it so routers receive the transformed body (register before routers in `app/main.py`). Keep logging middleware ordering intentional.
  - When touching auth tokens, prefer using existing helpers in `app/utils/jwt_utils.py` instead of reimplementing JWT logic.
  - When adding features that touch sessions or access logs, update `app/models/logs.py` and keep `logging_middleware` behavior consistent.

- **Examples to copy/paste**:
  - Register AES middleware in `app/main.py` (dev example):
    ```py
    from app.middleware.aes_gcm_middleware import aes_gcm_middleware
    app.middleware("http")(aes_gcm_middleware)
    ```
  - Client call pattern (from `app/client_example.py`):
    ```py
    from app.utils.aes_gcm_utils import encrypt_bytes
    body = encrypt_bytes(json.dumps(payload).encode())
    headers = {"X-Encrypted": "1", "Content-Type": "application/octet-stream"}
    requests.post(url, data=body, headers=headers)
    ```

- **Don't guess or break**:
  - Do not change database model field names without updating repositories and any code that constructs model instances.
  - Avoid changing the AES key handling — production must set `AESGCM_KEY` as base64.

If any section is unclear or you want more concrete examples (e.g., JWT internals, sample `.env`, or a small test harness), tell me which area to expand and I'll update this file.
