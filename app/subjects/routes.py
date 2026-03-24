from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.subjects.schemas import SubjectRead, SubjectCreate
from app.subjects.models import Subject
from app.core.database import SessionDep
from app.auths.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/subjects",
    tags=["subjects"]
)

@router.post("/", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject: SubjectCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    db_subject = Subject(**subject.model_dump())
    db_subject.owner_id = current_user.id

    try:
        session.add(db_subject)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una materia con ese nombre"
        )
    
    session.refresh(db_subject)

    return SubjectRead(
        **db_subject.model_dump(),
        difficulty_label=db_subject.difficulty.label
    )