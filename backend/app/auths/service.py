from sqlmodel import Session, select, desc
from app.users.models import User
from app.auths.models import RefreshToken
from app.core.security import (verify_password,
                               create_access_token,
                               create_refresh_token)
from app.core.config import settings
from app.core.database import SessionDep
from app.utils import utc_now
from datetime import timedelta, timezone

GRACE_PERIOD = timedelta(seconds=settings.REFRESH_TOKEN_GRACE_PERIOD)

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

def get_refresh_token(refresh_token: str, session: SessionDep) -> RefreshToken | None:
    return session.exec(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token
        ).order_by(desc(RefreshToken.id))
    ).first()

def is_token_revoked(token: RefreshToken) -> bool:
    return token.revoked_at is not None

def revoke_refresh_token(token: RefreshToken, session: SessionDep) ->  None:

    token.revoked_at = utc_now()
    session.add(token)
    session.commit()


def is_token_usable(token: RefreshToken) -> bool:
    if token.revoked_at is None:
        return True
    
    now = utc_now()

    revoked_at = token.revoked_at

    if revoked_at.tzinfo is None:
        revoked_at = revoked_at.replace(tzinfo=timezone.utc)

    if now - revoked_at < GRACE_PERIOD:
        return True
    
    return False

def new_refresh_token_db(user_id, new_refresh_token, expires_at, session: SessionDep) -> RefreshToken:
    refresh_token_db = RefreshToken(
        user_id=user_id,
        token=new_refresh_token,
        expires_at=expires_at
    )

    session.add(refresh_token_db)
    session.commit()
    session.refresh(refresh_token_db)
    return refresh_token_db
