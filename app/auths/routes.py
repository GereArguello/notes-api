from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.database import get_session, SessionDep
from app.core.security import decode_token
from app.auths.service import (authenticate_user,
                               generate_auth_tokens,
                               check_token_blacklist,
                               remove_refresh_token)
from app.auths.schemas import Token, RefreshTokenRequest
from app.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: Session = Depends(get_session)):
    
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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest, session: SessionDep):
    refresh_token = data.refresh_token
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token inválido")

    blacklisted = check_token_blacklist(session, refresh_token)

    if blacklisted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token revocado")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = session.get(User, int(user_id))

    if not user or user.deleted_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token inválido")

    new_access_token, new_refresh_token = generate_auth_tokens(user.id)

    exp = payload.get("exp")

    if not exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    blacklist = remove_refresh_token(refresh_token, exp)

    session.add(blacklist)
    session.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(refresh_token: str, session: SessionDep):
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token inválido")

    blacklisted = check_token_blacklist(session, refresh_token)

    if blacklisted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = "Token revocado")

    exp = payload.get("exp")

    if not exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    blacklist = remove_refresh_token(refresh_token, exp)

    session.add(blacklist)
    session.commit()

    return{"message": "Logout exitoso"}
