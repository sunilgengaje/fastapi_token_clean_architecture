# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserRead, Token
from app.services.auth_service import AuthService
from app.database import get_db
from app.services.session_service import create_session, end_session
from app.utils.logging_utils import get_client_ip

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, service: AuthService = Depends(), db: Session = Depends(get_db)):
    # service.register_user should create and return UserRead
    return service.register_user(user_in)

@router.post("/login", response_model=Token)
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    service: AuthService = Depends(),
):
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # create session record and set cookie
    ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")
    session_id = create_session(db=db, user_id=user.id, ip=ip, user_agent=user_agent)

    # set cookie (httpOnly)
    response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")

    # return token as before (service.create_login_token)
    token = service.create_login_token(user)
    return token

@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"detail": "no session"}
    end_session(db=db, session_id=session_id)
    from fastapi.responses import JSONResponse
    response = JSONResponse(content={"detail": "logged out"})
    response.delete_cookie("session_id")
    return response
