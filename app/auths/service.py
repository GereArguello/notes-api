from sqlmodel import Session, select
from app.users.models import User
from app.auths.models import TokenBlacklist
from app.core.security import (verify_password,
                               create_access_token,
                               create_refresh_token)
from app.core.config import settings
from app.core.database import SessionDep
from datetime import datetime, timezone, timedelta

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

def check_token_blacklist(session: SessionDep, refresh_token: str) -> TokenBlacklist | None :
    blacklisted = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.refresh_token == refresh_token)
    ).first()

    return blacklisted

def remove_refresh_token(refresh_token, exp):
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)

    return TokenBlacklist(
        refresh_token = refresh_token,
        expires_at= expires_at
    )