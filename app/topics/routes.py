from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page

from app.core.database import SessionDep
from app.core.pagination import TopicPagination
from app.subjects.models import Subject
from app.subjects.dependencies import get_user_subject
from app.topics.dependencies import get_user_topic
from app.topics.models import Topic
from app.topics.schemas import TopicCreate, TopicRead, TopicUpdate, TopicReOrder
from app.topics.services import (get_max_order_or_0,
                                get_topics_to_reorder)

from app.utils import utc_now, shift_items

router = APIRouter(tags=["topics"])


@router.post(
    "/subjects/{subject_id}/topics",
    response_model=TopicRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tema",
    description="""
Crea un nuevo tema dentro de una materia del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia (`subject`) pertenezca al usuario
- Recibe los datos del tema
- Calcula el `sort_order` automáticamente (al final de la lista)
- Guarda el tema en base de datos
- Retorna el tema creado

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia

### Notas
- El tema se crea siempre al final (orden incremental)
- El nombre del tema debe ser único dentro de la materia
- El orden (`sort_order`) se gestiona automáticamente

### Ejemplo
{
  "name": "Funciones"
}
""",
    responses={
        201: {
            "description": "Tema creado correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Materia no encontrada"
        },
        409: {
            "description": "Ya existe un tema con ese nombre en la materia"
        }
    }
)
def create_topic(
    topic: TopicCreate,
    session: SessionDep,
    subject: Subject = Depends(get_user_subject)
):
    db_topic = Topic(**topic.model_dump(), subject_id=subject.id)

    max_order = get_max_order_or_0(session, subject.id)

    db_topic.sort_order = max_order + 1

    try:
        session.add(db_topic)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un tema con este nombre"
        )
    session.refresh(db_topic)

    return db_topic

@router.get(
    "/subjects/{subject_id}/topics",
    response_model=Page[TopicRead],
    status_code=status.HTTP_200_OK,
    summary="Listar temas",
    description="""
Retorna una lista paginada de los temas pertenecientes a una materia del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia (`subject`) pertenezca al usuario
- Obtiene los temas asociados a la materia
- Ordena los resultados por `sort_order`
- Aplica paginación
- Retorna los resultados paginados

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia

### Query params
- `page`: número de página (default: 1)
- `size`: cantidad de elementos por página

### Notas
- Solo retorna temas de la materia del usuario autenticado
- Los resultados están ordenados por `sort_order`
- El orden refleja la posición manual definida por el usuario

### Estructura de respuesta
- `items`: lista de temas
- `total`: cantidad total de registros
- `page`: página actual
- `size`: tamaño de página
""",
    responses={
        200: {
            "description": "Listado de temas obtenido correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Materia no encontrada"
        }
    }
)
def list_topics(
    session: SessionDep,
    subject: Subject = Depends(get_user_subject),
    params: TopicPagination = Depends()
):
    
    qs = (
        select(Topic)
        .where(Topic.subject_id == subject.id)
        .order_by(Topic.sort_order)
    )

    return paginate(session, qs, params)

@router.get(
    "/subjects/{subject_id}/topics/{topic_id}",
    response_model=TopicRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener tema",
    description="""
Retorna un tema específico de una materia del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia y el tema pertenezcan al usuario
- Actualiza:
  - `topic.last_viewed_at`
  - `subject.last_viewed_at`
- Retorna el tema

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema

### Notas
- Solo permite acceder a recursos del usuario autenticado
- Si el tema no existe o no pertenece al usuario → error 404
- Cada acceso actualiza métricas de uso (`last_viewed_at`)
- También actualiza la materia asociada (tracking jerárquico)

### Resultado
Retorna el tema con todos sus campos, incluyendo timestamps relevantes
""",
    responses={
        200: {
            "description": "Tema obtenido correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Tema o materia no encontrada"
        }
    }
)
def read_topic(
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
):
    now = utc_now()

    topic.last_viewed_at = now
    topic.subject.last_viewed_at = now

    session.commit()
    session.refresh(topic)

    return topic

@router.patch(
    "/subjects/{subject_id}/topics/{topic_id}",
    response_model=TopicRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar tema",
    description="""
Actualiza parcialmente un tema de una materia del usuario autenticado.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia y el tema pertenezcan al usuario
- Obtiene los campos a actualizar (parciales)
- Verifica que haya datos para actualizar
- Si no hay cambios en el nombre, retorna directamente
- Aplica los cambios
- Guarda en base de datos
- Retorna el tema actualizado

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema

### Notas
- Solo se actualizan los campos enviados
- No es necesario enviar todos los campos
- El nombre debe ser único dentro de la materia
- Si no se envían datos → error 400
- Si se intenta usar un nombre ya existente → error 409

### Ejemplo
{
  "name": "Nuevo tema"
}
""",
    responses={
        200: {
            "description": "Tema actualizado correctamente"
        },
        400: {
            "description": "No se enviaron datos para actualizar"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Tema o materia no encontrada"
        },
        409: {
            "description": "Ya existe un tema con ese nombre"
        }
    }
)
def update_topic(
    session: SessionDep,
    topic_data: TopicUpdate,
    topic: Topic = Depends(get_user_topic),
):
    update_data = topic_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    if "name" in update_data and topic.name == update_data["name"]:
        return topic
    
    topic.sqlmodel_update(update_data)

    try:
        session.add(topic)
        session.commit()
        session.refresh(topic)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un tema con este nombre"
        )
    return topic

@router.patch(
    "/subjects/{subject_id}/topics/{topic_id}/re-order",
    response_model=TopicRead,
    status_code=status.HTTP_200_OK,
    summary="Reordenar tema",
    description="""
Cambia la posición (`sort_order`) de un tema dentro de una materia.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia y el tema pertenezcan al usuario
- Recibe el nuevo `sort_order`
- Valida:
  - que haya datos para actualizar
  - que el nuevo orden sea distinto al actual
  - que esté dentro del rango válido
- Obtiene los temas afectados por el cambio
- Reordena los temas intermedios
- Asigna la nueva posición al tema
- Guarda los cambios en base de datos

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema

### Body
{
  "sort_order": 3
}

### Notas
- El orden es relativo dentro de la materia
- Los demás temas se ajustan automáticamente
- Evita conflictos de unicidad en `sort_order`
- Si el nuevo orden es igual al actual, no se realizan cambios
- Si el orden está fuera de rango → error 400

### Ejemplo de comportamiento
- Mover de posición 2 → 4:
  - Los temas entre 3 y 4 se desplazan hacia arriba
- Mover de posición 4 → 2:
  - Los temas entre 2 y 3 se desplazan hacia abajo

### Resultado
Retorna el tema con su nueva posición (`sort_order`)
""",
    responses={
        200: {
            "description": "Tema reordenado correctamente"
        },
        400: {
            "description": "Datos inválidos o fuera de rango"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Tema o materia no encontrada"
        },
        409: {
            "description": "Conflicto al reordenar los temas"
        }
    }
)
def re_order_topic(
    order_data: TopicReOrder,
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
):
    data = order_data.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    new_sort_order = data["sort_order"]
    
    if topic.sort_order == new_sort_order:
        return topic

    last_topic = get_max_order_or_0(session, topic.subject_id)

    if new_sort_order > last_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de orden fuera de rango"
        )
    
    old_order = topic.sort_order

    topics = get_topics_to_reorder(session, topic.subject_id, old_order, new_sort_order)

    try:
        topic.sort_order = -1
        session.add(topic)
        session.flush()

        if new_sort_order > old_order:
            shift_items(session, topics, move_up=True)
        else:
            shift_items(session, topics, move_up=False)

        topic.sort_order = new_sort_order
        session.add(topic)
        
        session.commit()
        session.refresh(topic)

        return topic
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al reordenar los temas"
        )
    
@router.delete(
    "/subjects/{subject_id}/topics/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tema",
    description="""
Elimina un tema de una materia del usuario autenticado y ajusta el orden de los temas restantes.

### Flujo
- Extrae el `access_token` desde el header `Authorization`
- Valida el usuario autenticado
- Verifica que la materia y el tema pertenezcan al usuario
- Obtiene los temas con `sort_order` mayor al eliminado
- Elimina el tema
- Reordena los temas restantes para evitar huecos
- Persiste los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema

### Notas
- Solo permite eliminar temas del usuario autenticado
- Mantiene el orden continuo (`sort_order`) sin saltos
- Los temas posteriores se desplazan automáticamente

### Ejemplo de comportamiento
Si existen temas con orden:
1, 2, 3, 4

Y se elimina el tema con orden 2:
→ los restantes pasan a ser:
1, 2, 3

### Resultado
- No retorna contenido (`204 No Content`)
""",
    responses={
        204: {
            "description": "Tema eliminado correctamente"
        },
        401: {
            "description": "No autenticado o token inválido"
        },
        404: {
            "description": "Tema o materia no encontrada"
        }
    }
)
def delete_topic(
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
):
    topics_to_update = session.exec(
        select(Topic)
        .where(
            Topic.subject_id == topic.subject_id,
            Topic.sort_order > topic.sort_order
        )
    ).all()

    session.delete(topic)
    session.flush()

    shift_items(session, topics_to_update, move_up=True)    

    session.commit()

    return None

