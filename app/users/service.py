from sqlmodel import Session, update
from app.users.models import User
from app.auths.models import RefreshToken
from app.core.security import get_password_hash
from utils import utc_now

def update_user_service(user: User, data: dict, session: Session):
    user.sqlmodel_update(data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_password_service(user: User, new_password: str, session: Session):

    user.password_hash = get_password_hash(new_password)

    session.add(user)
    session.commit()
    session.refresh(user)

def revoke_all_refresh_tokens(user_id: int, session: Session):
    statement = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .values(revoked_at=utc_now())
    )

    session.exec(statement)
    session.commit()
    
    
