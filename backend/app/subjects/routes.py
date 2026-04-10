from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, desc
from typing import Literal
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page


from app.subjects.schemas import SubjectRead, SubjectCreate, SubjectUpdate
from app.subjects.models import Subject
from app.subjects.dependencies import get_user_subject

from app.core.database import SessionDep
from app.core.pagination import SubjectPagination
from app.auths.dependencies import get_current_user
from app.users.models import User
from app.utils import utc_now

router = APIRouter(
    prefix="/subjects",
    tags=["subjects"]
)

@router.post(
    "/",
    response_model=SubjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear materia",
    description="""
Crea una nueva materia asociada al usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Recibe los datos de la materia
- Asocia la materia al usuario (`owner_id`)
- Guarda la materia en base de datos
- Retorna la materia creada

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Notas
- El nombre de la materia debe ser único por usuario
- Se permite repetir nombres entre distintos usuarios
- Retorna un campo adicional `difficulty_label` (representación textual)

### Ejemplo
{
  "name": "Matemática",
  "description": "Apuntes de álgebra",
  "difficulty": 3
}

### Difficulty
Valores posibles:
- 1 -> Muy fácil
- 2 -> Fácil
- 3 -> Medio
- 4 -> Difícil
- 5 -> Muy difícil
""",
    responses={
        201: {
        "description": "Materia creada correctamente"
        },
        401: {
        "description": "No autenticado o token inválido"
        },
        409: {
        "description": "Ya existe una materia con ese nombre para el usuario"
        }
    }
)
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

@router.get(
    "/",
    response_model=Page[SubjectRead],
    status_code=status.HTTP_200_OK,
    summary="Listar materias",
    description="""
Retorna una lista paginada de las materias del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Obtiene todas las materias asociadas al usuario
- Aplica ordenamiento por fecha de creación
- Aplica paginación
- Retorna los resultados paginados

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Query params
- `page`: número de página (default: 1)
- `size`: cantidad de elementos por página (default según configuración)
- `order`: orden por fecha de creación
  - `desc` (default): más recientes primero
  - `asc`: más antiguos primero

### Notas
- Solo retorna materias del usuario autenticado
- Los resultados están paginados
- El orden se aplica sobre `created_at`

### Estructura de respuesta
- `items`: lista de materias
- `total`: cantidad total de registros
- `page`: página actual
- `size`: tamaño de página
""",
    responses={
        200: {
            "description": "Listado de materias obtenido correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        }
    }
)
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

@router.get(
    "/{subject_id}",
    response_model=SubjectRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener materia",
    description="""
Retorna una materia específica del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia pertenezca al usuario
- Actualiza el campo `last_viewed_at`
- Retorna la materia

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia

### Notas
- Solo permite acceder a materias del usuario autenticado
- Si la materia no existe o no pertenece al usuario → error 404
- Cada acceso actualiza `last_viewed_at` (tracking de uso)

### Resultado
Retorna la materia con todos sus campos, incluyendo:
- `difficulty_label`
- timestamps (`created_at`, `updated_at`, `last_viewed_at`)
""",
    responses={
        200: {
            "description": "Materia obtenida correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Materia no encontrada"
        }
    }
)
def read_subject(
    session: SessionDep,
    subject: Subject = Depends(get_user_subject),
):

    subject.last_viewed_at = utc_now()

    session.commit()
    session.refresh(subject)
    
    return subject

@router.patch(
    "/{subject_id}",
    response_model=SubjectRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar materia",
    description="""
Actualiza parcialmente una materia del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Busca la materia por ID y verifica que pertenezca al usuario
- Obtiene los campos a actualizar (parciales)
- Si no hay cambios en el nombre, retorna directamente
- Aplica los cambios
- Guarda en base de datos
- Retorna la materia actualizada

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia

### Notas
- Solo se actualizan los campos enviados
- No es necesario enviar todos los campos
- El nombre debe ser único por usuario
- Si se intenta usar un nombre ya existente → error 409

### Ejemplo
{
  "name": "Nueva materia",
  "description": "Nuevo contenido"
}
""",
    responses={
        200: {
            "description": "Materia actualizada correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Materia no encontrada"
        },
        409: {
            "description": "Ya existe una materia con ese nombre"
        }
    }
)
def update_subject(
    session: SessionDep,
    subject_id: int,
    subject_data: SubjectUpdate,
    current_user: User = Depends(get_current_user)
):
    subject = session.exec(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.owner_id == current_user.id
        )
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La materia no existe"
        )
    
    update_data = subject_data.model_dump(exclude_unset=True)

    if "name" in update_data and subject.name == update_data["name"]:
        return subject

    subject.sqlmodel_update(update_data)

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

@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar materia",
    description="""
Elimina una materia del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Busca la materia por ID y verifica que pertenezca al usuario
- Elimina la materia de la base de datos
- Persiste los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia

### Notas
- Solo permite eliminar materias del usuario autenticado
- Si la materia no existe o no pertenece al usuario → error 404
- Esta acción elimina también los datos relacionados según configuración de la base de datos (cascade)

### Resultado
- No retorna contenido (`204 No Content`)
""",
    responses={
        204: {
            "description": "Materia eliminada correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Materia no encontrada"
        }
    }
)
def delete_subject(
    session: SessionDep,
    subject_id: int,
    current_user: User = Depends(get_current_user)
):
    subject = session.exec(
        select(Subject).where(
            Subject.id == subject_id,
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