from sqlmodel import Session, select
from app.users.models import User
from app.auths.models import RefreshToken
from app.core.security import (verify_password,
                               create_access_token,
                               create_refresh_token)
from app.core.config import settings
from app.core.database import SessionDep
from datetime import timedelta

def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()

def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email)

    if not user:
        return None
    
    if user.deleted_at:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def generate_auth_tokens(user_id: int):

    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return access_token, refresh_token

def is_token_revoked(refresh_token: str, session: SessionDep) -> bool:
    token = session.exec(
        select(RefreshToken).where(
            (RefreshToken.token == refresh_token) &
            (RefreshToken.revoked == True)
        )
    ).first()

    return token is not None

def revoke_refresh_token(refresh_token, session: SessionDep) -> RefreshToken | None:
    token = session.exec(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    ).first()
    
    if not token:
        return None
    
    token.revoked = True
    session.add(token)
    session.commit()

    return token

def is_refresh_token_in_db(refresh_token: str, session: SessionDep) -> bool:
    token_in_db = session.exec(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token
        )
    ).first()

    return token_in_db is not None