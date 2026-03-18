from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from app.users.schemas import UserCreate, UserRead, UserUpdate, UserUpdatePassword
from app.users.models import User
from app.users.service import (update_user_service,
                               update_password_service,
                               revoke_all_refresh_tokens)
from app.core.database import SessionDep
from app.core.security import get_password_hash, verify_password
from app.utils import utc_now
from app.auths.dependencies import get_current_user



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

@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(update_data: UserUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    
    if not update_data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar"
        )
    
    return update_user_service(current_user, update_data, session)

@router.patch("/me/password",
              status_code=status.HTTP_200_OK)
def update_password(
                    password_data: UserUpdatePassword,
                    session: SessionDep,
                    current_user: User = Depends(get_current_user)
):
    
    if password_data.new_password != password_data.new_password2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Las contraseñas no coinciden"
        )
    
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña no puede ser igual a la actual"
        )
    
    update_password_service(current_user, password_data.new_password, session)

    revoke_all_refresh_tokens(current_user.id, session)


    return {"message": "Contraseña actualizada correctamente"}

@router.patch("/me/deactivate", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(session: SessionDep, current_user: User = Depends(get_current_user)):
        
    if not current_user.deleted_at:
        current_user.deleted_at = utc_now()
        revoke_all_refresh_tokens(current_user.id, session)
        session.commit()



@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(session: SessionDep, current_user: User = Depends(get_current_user)):

    revoke_all_refresh_tokens(current_user.id, session)

    session.delete(current_user)
    session.commit()