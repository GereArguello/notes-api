from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, desc
from typing import Literal
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page


from app.subjects.schemas import SubjectRead, SubjectCreate, SubjectUpdate
from app.subjects.models import Subject
from app.core.database import SessionDep
from app.core.pagination import SubjectPagination
from app.auths.dependencies import get_current_user
from app.users.models import User
from app.utils import utc_now

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

@router.get("/{subj_id}", response_model=SubjectRead, status_code=status.HTTP_200_OK)
def read_subject(
    session: SessionDep,
    subj_id: int,
    current_user: User = Depends(get_current_user)
):
    subject = session.exec(
        select(Subject)
        .where(Subject.id == subj_id, Subject.owner_id == current_user.id)
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La materia no existe"
        )
    
    subject.last_viewed_at = utc_now()
    session.add(subject)
    session.commit()
    session.refresh(subject)
    
    return subject

@router.patch("/{subj_id}", response_model=SubjectRead, status_code=status.HTTP_200_OK)
def update_subject(
    session: SessionDep,
    subj_id: int,
    subject_data: SubjectUpdate,
    current_user: User = Depends(get_current_user)
):
    subject = session.exec(
        select(Subject).where(
            Subject.id == subj_id,
            Subject.owner_id == current_user.id
        )
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La materia no existe"
        )
    
    updated_data = subject_data.model_dump(exclude_unset=True)

    subject.sqlmodel_update(updated_data)

    try:
        session.add(subject)
        session.commit()
        session.refresh(subject)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una materia con ese nombre"
        )
    return subject

@router.delete("/{subj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    session: SessionDep,
    subj_id: int,
    current_user: User = Depends(get_current_user)
):
    subject = session.exec(
        select(Subject).where(
            Subject.id == subj_id,
            Subject.owner_id == current_user.id
        )
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La materia no existe"
        )
    
    session.delete(subject)
    session.commit()
    
    return None