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
import logging

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="""
Crea un nuevo usuario en el sistema.

### Flujo
- Recibe los datos del usuario
- Valida que `password` y `password2` coincidan
- Hashea la contraseña
- Crea el usuario en base de datos
- Retorna el usuario creado (sin contraseña)

### Notas
- El email debe ser único
- La contraseña nunca se almacena en texto plano
- Se guarda únicamente el `password_hash`

### Validaciones
- Si las contraseñas no coinciden → error 422
- Si el email ya existe → error 409
""",
    responses={
        201: {
            "description": "Usuario creado correctamente"
        },
        422: {
            "description": "Las contraseñas no coinciden o datos inválidos"
        },
        409: {
            "description": "El email ya está registrado"
        }
    }
)
def create_user(
    user_data: UserCreate,
    session: SessionDep
):
    logger.info(f"Intento de registro: {user_data.email}")

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

        logger.info(f"Usuario creado correctamente: {user.email}")
        return user
    
    except IntegrityError:
        session.rollback()

        logger.warning(f"Email ya registrado: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )
    except Exception as e:
        session.rollback()

        logger.exception("Error inesperado en create_user")  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno"
        )

@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    description="""
Retorna la información del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el token
- Obtiene el usuario asociado
- Retorna los datos del usuario

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Notas
- No requiere parámetros
- No expone información sensible como la contraseña
- Si el token es inválido o expirado, se retorna 401
""",
    responses={
        200: {
            "description": "Datos del usuario autenticado"
        },
        401: {
            "description": "No autenticado o token inválido"
        }
    }
)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
    description="""
Actualiza parcialmente los datos del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Recibe los campos a actualizar (parciales)
- Verifica que haya al menos un campo para actualizar
- Aplica los cambios en base de datos
- Retorna el usuario actualizado

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Notas
- Solo se actualizan los campos enviados
- No es necesario enviar todos los campos
- Si no se envían datos → error 400

### Ejemplo
{
  "first_name": "Nuevo nombre"
}
""",
    responses={
        200: {
        "description": "Usuario actualizado correctamente"
        },
        400: {
        "description": "No se enviaron datos para actualizar"
        },
        401: {
        "description": "No autenticado o token inválido"
        }
    }
)
def update_user(update_data: UserUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    
    if not update_data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar"
        )
    
    return update_user_service(current_user,
                               update_data.model_dump(exclude_unset=True),
                               session)

@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Actualizar contraseña",
    description="""
Actualiza la contraseña del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica:
  - que la contraseña actual sea correcta
  - que las nuevas contraseñas coincidan
  - que la nueva contraseña sea distinta a la actual
- Actualiza la contraseña (hash)
- Revoca todos los `refresh_tokens` del usuario (cierre de sesiones activas)
- Retorna un mensaje de confirmación

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Seguridad
- La contraseña se almacena hasheada
- Se invalidan todas las sesiones activas tras el cambio
- Evita reutilización de la misma contraseña

### Ejemplo
{
  "current_password": "password_actual",
  "new_password": "nueva_password",
  "new_password2": "nueva_password"
}
""",
    responses={
        200: {
        "description": "Contraseña actualizada correctamente"
        },
        400: {
        "description": "Contraseña actual incorrecta o nueva contraseña inválida"
        },
        422: {
        "description": "Las contraseñas no coinciden"
        },
        401: {
        "description": "No autenticado o token inválido"
        }
    }
)
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

@router.patch(
    "/me/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar usuario",
    description="""
Desactiva la cuenta del usuario autenticado (soft delete).

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Marca el usuario como eliminado (`deleted_at`)
- Revoca todos los `refresh_tokens` del usuario
- Persiste los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Notas
- No elimina físicamente el usuario de la base de datos
- El usuario queda inhabilitado para futuras autenticaciones
- Todas las sesiones activas se invalidan inmediatamente
- Si el usuario ya está desactivado, no se realizan cambios

### Resultado
- No retorna contenido (`204 No Content`)
""",
    responses={
        204: {
            "description": "Usuario desactivado correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        }
    }
)
def deactivate_user(session: SessionDep, current_user: User = Depends(get_current_user)):
        
    if not current_user.deleted_at:
        current_user.deleted_at = utc_now()
        revoke_all_refresh_tokens(current_user.id, session)
        session.commit()


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="""
Elimina permanentemente la cuenta del usuario autenticado (hard delete).

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Revoca todos los `refresh_tokens` del usuario
- Elimina el usuario de la base de datos
- Persiste los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Notas
- Esta acción es **irreversible**
- A diferencia de `/me/deactivate`, elimina completamente el registro
- Todas las sesiones activas se invalidan inmediatamente

### Resultado
- No retorna contenido (`204 No Content`)
""",
    responses={
        204: {
            "description": "Usuario eliminado correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        }
    }
)
def delete_user(session: SessionDep, current_user: User = Depends(get_current_user)):

    revoke_all_refresh_tokens(current_user.id, session)

    session.delete(current_user)
    session.commit()