from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlmodel import select
from app.core.database import SessionDep
from app.auths.dependencies import get_current_user
from app.users.models import User
from app.pages.dependencies import get_user_page
from app.pages.models import Page
from app.tags.schemas import TagCreate, TagRead
from app.tags.models import Tag
from app.tags.services import get_tag_or_create
from app.page_tags.services import attach_tag_to_page
from app.page_tags.models import PageTagLink
from app.core.limiter import limiter



router = APIRouter(tags=["tags"])

@router.post(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar tag a página",
    description="""
Crea o reutiliza un tag y lo asocia a una página del usuario autenticado.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia, tema y página pertenezcan al usuario
- Normaliza el nombre del tag (trim + lowercase)
- Busca el tag existente o lo crea
- Asocia el tag a la página
- Persiste los cambios
- Retorna el tag

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema
- `page_id`: ID de la página

### Body
{
  "name": "backend"
}

### Notas
- Los tags son únicos por usuario
- Se reutilizan si ya existen
- La relación página-tag evita duplicados

### Resultado
Retorna el tag asociado
""",
    responses={
        201: {"description": "Tag creado/asociado correctamente"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Página, tema o materia no encontrada"},
    }
)
@limiter.limit("60/minute")
def create_tag(
    request: Request,
    data: TagCreate,
    session: SessionDep,
    page: Page = Depends(get_user_page)
):
    tag_name = data.name.strip().lower()
    user_id = page.topic.subject.owner_id

    tag = get_tag_or_create(session, user_id, tag_name)

    attach_tag_to_page(session, page.id, tag.id)

    session.commit()

    return tag

@router.get(
    "/tags",
    response_model=list[TagRead],
    status_code=status.HTTP_200_OK,
    summary="Listar tags",
    description="""
Retorna todos los tags del usuario autenticado, con opción de búsqueda.

### Flujo
- Valida el usuario autenticado
- Obtiene los tags asociados al usuario
- Aplica filtro opcional por nombre (`search`)
- Ordena alfabéticamente
- Retorna la lista de tags

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Query params
- `search`: filtro opcional por nombre (case-insensitive parcial)

### Notas
- Solo retorna tags del usuario autenticado
- El filtro busca coincidencias parciales en el nombre
- Los resultados se ordenan por nombre

### Resultado
Retorna una lista de tags
""",
    responses={
        200: {"description": "Listado de tags obtenido correctamente"},
        401: {"description": "No autenticado o token inválido"}
    }
)
@limiter.limit("60/minute")
def list_tags(
    request: Request,
    session: SessionDep,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
):
    query = select(Tag).where(Tag.owner_id == current_user.id)

    if search:
        query = query.where(Tag.name.contains(search.lower()))

    query = query.order_by(Tag.name)

    return session.exec(query).all()

@router.delete(
    "/subjects/{subject_id}/topics/{topic_id}/pages/{page_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tag de página",
    description="""
Elimina la asociación entre un tag y una página del usuario autenticado.

### Flujo
- Valida el usuario autenticado
- Verifica que la materia, tema y página pertenezcan al usuario
- Busca la relación entre la página y el tag
- Si existe, elimina la asociación
- Persiste los cambios

### Autenticación requerida
- Header: `Authorization: Bearer <access_token>`

### Path params
- `subject_id`: ID de la materia
- `topic_id`: ID del tema
- `page_id`: ID de la página
- `tag_id`: ID del tag

### Notas
- Solo elimina la relación, no el tag en sí
- Si el tag no está asociado a la página → error 404

### Resultado
- No retorna contenido (`204 No Content`)
""",
    responses={
        204: {"description": "Tag eliminado de la página correctamente"},
        401: {"description": "No autenticado o token inválido"},
        404: {"description": "Relación página-tag no encontrada"}
    }
)
@limiter.limit("60/minute")
def delete_page_tag(
    request: Request,
    tag_id: int,
    session: SessionDep,
    page: Page = Depends(get_user_page),
):
    link = session.exec(
        select(PageTagLink).where(
            PageTagLink.page_id == page.id,
            PageTagLink.tag_id == tag_id
        )
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El tag no está asociado a esta página"
        )
    
    session.delete(link)
    session.commit()
