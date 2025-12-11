# app/routers/echo_router.py
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/echo")
async def echo(request: Request):
    # body is already decrypted by middleware if X-Encrypted header present
    data = await request.json()
    # process normally
    return {"received": data, "ok": True}
