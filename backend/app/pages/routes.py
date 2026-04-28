from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page as PageResponse

from app.core.database import SessionDep
from app.core.pagination import PagePagination
from app.topics.models import Topic
from app.pages.schemas import PageRead, PageCreate, PageUpdate, PageReOrder
from app.pages.models import Page
from app.topics.dependencies import get_user_topic
from app.pages.dependencies import get_user_page
from app.pages.services import get_max_order_or_0, get_pages_to_reorder
from app.utils import utc_now, shift_items
from app.core.limiter import limiter


router = APIRouter(tags=["pages"])


@router.post(
    "/subjects/{subject_id}/topics/{topic_id}/pages",
    response_model=PageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear página",
    description="""
Crea una nueva página dentro de un tema del usuario autenticado.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia y el tema pertenezcan al usuario
- Recibe los datos de la página
- Asigna automáticamente el `sort_order` al final
- Guarda la página en base de datos
- Retorna la página creada

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema

### Notas
- El nombre de la página debe ser único dentro del tema
- El orden (`sort_order`) se gestiona automáticamente

### Ejemplo
{
  "title": "Introducción",
  "content": "Contenido inicial"
}
""",
    responses={
        201: {"description": "Página creada correctamente"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Tema o materia no encontrada"},
        409: {"description": "Ya existe una página con ese nombre"}
    }
)
@limiter.limit("60/minute")
def create_page(
    request: Request,
    page_data: PageCreate,
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
):   
    db_page = Page(**page_data.model_dump(), topic_id=topic.id)

    max_order = get_max_order_or_0(session, topic.id)

    db_page.sort_order = max_order + 1

    try:
        session.add(db_page)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una página con este nombre"
        )
    
    session.refresh(db_page)

    return db_page

@router.get(
    "/subjects/{subject_id}/topics/{topic_id}/pages",
    response_model=PageResponse[PageRead],
    status_code=status.HTTP_200_OK,
    summary="Listar páginas",
    description="""
Retorna una lista paginada de las páginas de un tema del usuario autenticado.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia y el tema pertenezcan al usuario
- Obtiene las páginas del tema
- Ordena por `sort_order`
- Aplica paginación
- Retorna los resultados

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema

### Query params
- `page`: número de página
- `size`: cantidad de elementos por página

### Notas
- Solo retorna páginas del tema del usuario autenticado
- El orden refleja la posición definida (`sort_order`)

### Estructura de respuesta
- `items`: lista de páginas
- `total`: total de registros
- `page`: página actual
- `size`: tamaño de página
""",
    responses={
        200: {"description": "Listado de páginas obtenido correctamente"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Tema o materia no encontrada"}
    }
)
@limiter.limit("60/minute")
def list_pages(
    request: Request,
    session: SessionDep,
    topic: Topic = Depends(get_user_topic),
    params: PagePagination = Depends()
):
    qs = (
        select(Page)
        .where(Page.topic_id == topic.id)
        .order_by(Page.sort_order)
    )

    return paginate(session, qs, params)

@router.get(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
    response_model=PageRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener página",
    description="""
Retorna una página específica de un tema del usuario autenticado.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia, tema y página pertenezcan al usuario
- Actualiza:
  - `page.last_viewed_at`
  - `topic.last_viewed_at`
  - `subject.last_viewed_at`
- Retorna la página

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema
- `page_id`: ID de la página

### Notas
- Solo permite acceso a recursos del usuario autenticado
- Si la página no existe o no pertenece al usuario → error 404
- Actualiza métricas de uso en toda la jerarquía

### Resultado
Retorna la página con todos sus campos
""",
    responses={
        200: {"description": "Página obtenida correctamente"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Página, tema o materia no encontrada"}
    }
)
@limiter.limit("60/minute")
def read_page(
    request: Request,
    session: SessionDep,
    page: Page = Depends(get_user_page),
):

    now = utc_now()

    page.last_viewed_at = now
    page.topic.last_viewed_at = now
    page.topic.subject.last_viewed_at = now

    session.commit()
    session.refresh(page)

    return page

@router.patch(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
    response_model=PageRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar página",
    description="""
Actualiza parcialmente una página de un tema del usuario autenticado.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia, tema y página pertenezcan al usuario
- Obtiene los campos a actualizar (parciales)
- Verifica que haya datos para actualizar
- Si no hay cambios, retorna directamente
- Aplica los cambios
- Guarda en base de datos
- Retorna la página actualizada

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema
- `page_id`: ID de la página

### Notas
- Solo se actualizan los campos enviados
- No es necesario enviar todos los campos
- Si no se envían datos → error 400
- Si se intenta usar un título ya existente → error 409

### Ejemplo
{
  "title": "Nuevo título",
  "content": "Nuevo contenido"
}
""",
    responses={
        200: {"description": "Página actualizada correctamente"},
        400: {"description": "No se enviaron datos para actualizar"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Página, tema o materia no encontrada"},
        409: {"description": "Ya existe una página con ese título"}
    }
)
@limiter.limit("60/minute")
def update_page(
    request: Request,
    page_data: PageUpdate,
    session: SessionDep,
    page: Page = Depends(get_user_page)
):
    update_data = page_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )
    
    if all(getattr(page, k) == v for k, v in update_data.items()):
        return page
    
    page.sqlmodel_update(update_data)

    try:
        session.add(page)
        session.commit()
        session.refresh(page)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una página con este título"
        )
    return page

@router.patch(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/re-order",
    response_model=PageRead,
    status_code=status.HTTP_200_OK,
    summary="Reordenar página",
    description="""
Cambia la posición (`sort_order`) de una página dentro de un tema.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia, tema y página pertenezcan al usuario
- Recibe el nuevo `sort_order`
- Valida:
  - que haya datos para actualizar
  - que el nuevo orden sea distinto al actual
  - que esté dentro del rango válido
- Obtiene las páginas afectadas
- Reordena las páginas intermedias
- Asigna la nueva posición
- Guarda los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema
- `page_id`: ID de la página

### Body
{
  "sort_order": 3
}

### Notas
- El orden es relativo dentro del tema
- Las demás páginas se ajustan automáticamente
- Si el orden es igual al actual, no hay cambios
- Si está fuera de rango → error 400

### Resultado
Retorna la página con su nueva posición
""",
    responses={
        200: {"description": "Página reordenada correctamente"},
        400: {"description": "Datos inválidos o fuera de rango"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Página, tema o materia no encontrada"},
        409: {"description": "Conflicto al reordenar las páginas"}
    }
)
@limiter.limit("60/minute")
def re_order_page(
    request: Request,
    session: SessionDep,
    order_data: PageReOrder,
    page: Page = Depends(get_user_page)
):
    data = order_data.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    new_sort_order = data["sort_order"]

    if page.sort_order == new_sort_order:
        return page
    
    last_order = get_max_order_or_0(session, page.topic_id)

    if new_sort_order > last_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de orden fuera de rango"
        )
    
    old_order = page.sort_order

    pages = get_pages_to_reorder(session, page.topic_id, old_order, new_sort_order)

    try:
        page.sort_order = -1
        session.add(page)
        session.flush()

        if new_sort_order > old_order:
            shift_items(session, pages, move_up=True)
        else:
            shift_items(session, pages, move_up=False)

        page.sort_order = new_sort_order
        session.add(page)
        
        session.commit()
        session.refresh(page)

        return page
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al reordenar las páginas"
        )

@router.delete(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar página",
    description="""
Elimina una página de un tema del usuario autenticado y ajusta el orden de las páginas restantes.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia, tema y página pertenezcan al usuario
- Obtiene las páginas con `sort_order` mayor a la eliminada
- Elimina la página
- Reordena las páginas restantes para evitar huecos
- Persiste los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema
- `page_id`: ID de la página

### Notas
- Solo permite eliminar páginas del usuario autenticado
- Mantiene el orden continuo (`sort_order`)
- Las páginas posteriores se desplazan automáticamente

### Ejemplo de comportamiento
Si existen páginas con orden:
1, 2, 3, 4

Y se elimina la página con orden 2:
→ los restantes pasan a ser:
1, 2, 3

### Resultado
- No retorna contenido (`204 No Content`)
""",
    responses={
        204: {"description": "Página eliminada correctamente"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Página, tema o materia no encontrada"}
    }
)
@limiter.limit("60/minute")
def delete_page(
    request: Request,
    session: SessionDep,
    page: Page = Depends(get_user_page)
): 
    pages_to_update = (session.exec(
        select(Page)
        .where(
            Page.topic_id == page.topic_id,
            Page.sort_order > page.sort_order)
        )
    ).all()

    session.delete(page)
    session.flush()

    shift_items(session, pages_to_update, move_up=True)

    session.commit()

    return None
