from fastapi import status, HTTPException, Depends
from sqlmodel import select
from app.auths.dependencies import get_current_user
from app.core.database import SessionDep
from app.users.models import User
from app.subjects.models import Subject


def get_user_subject(
    subject_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    subject = session.exec(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.owner_id == current_user.id
        )
    ).first()

    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "La materia no existe")

    return subject