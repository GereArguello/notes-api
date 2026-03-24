from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, desc
from typing import Literal
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page


from app.subjects.schemas import SubjectRead, SubjectCreate
from app.subjects.models import Subject
from app.core.database import SessionDep
from app.core.pagination import SubjectPagination
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

@router.get("/", response_model=Page[SubjectRead], status_code=status.HTTP_200_OK)
def list_subjects(
    session: SessionDep,
    order: Literal["desc", "asc"] = "desc",
    current_user: User = Depends(get_current_user),
    params: SubjectPagination = Depends()
):
    qs = select(Subject).where(Subject.owner_id == current_user.id)

    if order == "asc":
        qs = qs.order_by(Subject.created_at)
    else:
        qs = qs.order_by(desc(Subject.created_at))

    return paginate(session, qs, params)