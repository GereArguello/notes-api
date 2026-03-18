from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import  SessionDep
from app.core.security import decode_token
from app.auths.service import (authenticate_user,
                               generate_auth_tokens,
                               is_token_revoked,
                               revoke_refresh_token,
                               is_refresh_token_in_db,
                               new_refresh_token_db)
from app.auths.schemas import Token
from app.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(response: Response, session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    access_token, refresh_token = generate_auth_tokens(user.id)

 
    payload = decode_token(refresh_token)
    exp = payload.get("exp")

    if not exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)

    new_refresh_token_db(user.id, refresh_token, expires_at, session)

    # cookie segura
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(
    session: SessionDep,
    response: Response,
    refresh_token: str = Cookie(None),
):
 
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )
    
    if not is_refresh_token_in_db(refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    if is_token_revoked(refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    payload = decode_token(refresh_token)

    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = session.get(User, int(user_id))

    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    # revocar token viejo
    revoke_refresh_token(refresh_token, session)

    # generar nuevos
    new_access_token, new_refresh_token = generate_auth_tokens(user.id)

    payload_new = decode_token(new_refresh_token)
    exp_new = payload_new.get("exp")

    expires_at = datetime.fromtimestamp(exp_new, tz=timezone.utc)

    new_refresh_token_db(user.id, new_refresh_token, expires_at, session)

    # setear cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    session: SessionDep,
    response: Response,
    refresh_token: str = Cookie(None)
):

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    if not is_refresh_token_in_db(refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    if is_token_revoked(refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    payload = decode_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token inválido")

    # revocar token 
    revoke_refresh_token(refresh_token, session)

    response.delete_cookie(
        key="refresh_token",
        secure=settings.COOKIE_SECURE,
        samesite="lax"
    )

    return
