from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.users.schemas import UserCreate, UserRead, UserUpdate, UserUpdatePassword
from app.users.models import User
from app.core.database import SessionDep
from app.core.security import get_password_hash, verify_password
from app.utils import utc_now



router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    session: SessionDep
):
    if user_data.password != user_data.password2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Las contraseñas no coinciden"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
            **user_data.model_dump(exclude={"password", "password2"}),
            password_hash=hashed_password
    )

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )

@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)

    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.patch("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_data: UserUpdate, session: SessionDep):

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    user.sqlmodel_update(update_data)

    session.commit()
    session.refresh(user)

    return user

@router.patch("/{user_id}/update-password",
              status_code=status.HTTP_200_OK)
def update_password(user_id: int,
                    password_data: UserUpdatePassword,
                    session: SessionDep):
    
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario está desactivado"
        )
    
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    if verify_password(password_data.new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña no puede ser igual a la actual"
        )
    
    if password_data.new_password != password_data.new_password2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Las contraseñas no coinciden"
        )
    
    user.password_hash = get_password_hash(password_data.new_password)

    session.commit()
    session.refresh(user)

    return {"message": "Contraseña actualizada correctamente"}

@router.patch("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_user(user_id: int, session: SessionDep):
    
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está desactivado"
        )

    user.deleted_at = utc_now()

    session.commit()

    return {"message": "Usuario desactivado"}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDep):

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    session.delete(user)
    session.commit()