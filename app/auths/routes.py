from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose.exceptions import JWTError
from datetime import datetime, timezone


from app.core.database import  SessionDep
from app.core.security import decode_token
from app.auths.service import (authenticate_user,
                               generate_auth_tokens,
                               is_token_revoked,
                               revoke_refresh_token,
                               is_refresh_token_in_db)
from app.auths.schemas import Token, RefreshTokenRequest
from app.auths.models import RefreshToken
from app.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    
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

    refresh_token_db = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at
    )

    session.add(refresh_token_db)
    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest, session: SessionDep):
    incoming_refresh_token = data.refresh_token


    payload = decode_token(incoming_refresh_token)

    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    if not is_refresh_token_in_db(incoming_refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    if is_token_revoked(incoming_refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado"
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
    revoke_refresh_token(incoming_refresh_token, session)

    # generar nuevos
    new_access_token, new_refresh_token = generate_auth_tokens(user.id)

    payload_new = decode_token(new_refresh_token)
    exp_new = payload_new.get("exp")

    expires_at = datetime.fromtimestamp(exp_new, tz=timezone.utc)

    refresh_token_db = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=expires_at
    )

    session.add(refresh_token_db)
    session.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: RefreshTokenRequest, session: SessionDep):
    refresh_token = data.refresh_token

    payload = decode_token(refresh_token)


    if not is_refresh_token_in_db(refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    if is_token_revoked(refresh_token, session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado"
        )
    

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token inválido")

    # revocar token 
    revoke_refresh_token(refresh_token, session)

    return
