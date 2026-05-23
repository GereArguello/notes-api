import { useCallback, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import { usePaginatedResource } from "../../hooks/usePaginatedResource";

import ListItem from "../../components/ListItem";
import ReorderModal from "../../components/ReorderModal";
import SectionHeader from "../../components/SectionHeader";
import PaginationFooter from "../../components/PaginationFooter";
import { getErrorMessage } from "../../utils/errorMessage";
import { showAlertOnce } from "../../utils/showAlertOnce";

function PagesPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const reorderResetTimeoutRef = useRef(null);
  const [movingPageIds, setMovingPageIds] = useState([]);
  const [pageToMove, setPageToMove] = useState(null);

  const fetchPages = useCallback(
    async (page) => {
      await fetchWithAuth(`/subjects/${subject_id}/topics/${topic_id}`, token);

      return fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages?page=${page}`,
        token
      );
    },
    [subject_id, topic_id, token]
  );

  const deletePage = useCallback(
    (pageId) =>
      fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages/${pageId}`,
        token,
        { method: "DELETE" }
      ),
    [subject_id, topic_id, token]
  );

  const {
    items: pages,
    loading,
    currentPage,
    hasPreviousPage,
    hasNextPage,
    totalItems,
    goToPage,
    handleDelete,
    updateItems,
    refetch,
  } = usePaginatedResource({
    pageSize: 20,
    fetchDataFn: fetchPages,
    deleteFn: deletePage,
  });

  const reorderPage = async (pageId, sortOrder) => {
    await fetchWithAuth(
      `/subjects/${subject_id}/topics/${topic_id}/pages/${pageId}/re-order`,
      token,
      {
        method: "PATCH",
        body: JSON.stringify({ sort_order: sortOrder }),
      }
    );

    await refetch();
  };

  const pulseMovingPages = (...ids) => {
    if (reorderResetTimeoutRef.current) {
      window.clearTimeout(reorderResetTimeoutRef.current);
    }

    setMovingPageIds(ids);
    reorderResetTimeoutRef.current = window.setTimeout(() => {
      setMovingPageIds([]);
    }, 260);
  };

  const handleStepMove = async (page, direction) => {
    const nextSortOrder = page.sort_order + direction;

    if (nextSortOrder < 1 || nextSortOrder > totalItems) {
      return;
    }

    const currentIndex = pages.findIndex((item) => item.id === page.id);
    const swapIndex = currentIndex + direction;
    const swapTarget = pages[swapIndex];

    if (swapTarget && swapTarget.sort_order === nextSortOrder) {
      const previousPages = pages;
      const reorderedPages = [...pages];

      reorderedPages[currentIndex] = {
        ...swapTarget,
        sort_order: page.sort_order,
      };
      reorderedPages[swapIndex] = {
        ...page,
        sort_order: nextSortOrder,
      };

      updateItems(reorderedPages);
      pulseMovingPages(page.id, swapTarget.id);

      try {
        await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}/re-order`,
          token,
          {
            method: "PATCH",
            body: JSON.stringify({ sort_order: nextSortOrder }),
          }
        );
      } catch (error) {
        updateItems(previousPages);
        setMovingPageIds([]);
        showAlertOnce(getErrorMessage(error, "No se pudo reordenar la pagina"));
      }

      return;
    }

    try {
      await reorderPage(page.id, nextSortOrder);
    } catch (error) {
      showAlertOnce(getErrorMessage(error, "No se pudo reordenar la pagina"));
    }
  };

  const confirmMoveTo = async (nextSortOrder) => {
    if (!pageToMove) return;

    if (!Number.isInteger(nextSortOrder)) {
      showAlertOnce("Ingresa un numero entero valido.");
      return;
    }

    if (nextSortOrder < 1 || nextSortOrder > totalItems) {
      showAlertOnce(`La posicion debe estar entre 1 y ${totalItems}.`);
      return;
    }

    if (nextSortOrder === pageToMove.sort_order) {
      setPageToMove(null);
      return;
    }

    try {
      await reorderPage(pageToMove.id, nextSortOrder);
      setPageToMove(null);
    } catch (error) {
      showAlertOnce(getErrorMessage(error, "No se pudo reordenar la pagina"));
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div className="page-container">
      <SectionHeader
        title="Paginas"
        subtitle="Abri cada hoja para leer, editar y seguir escribiendo."
      />

      <div className="list-container">
        <button
          type="button"
          onClick={() =>
            navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/new`)
          }
        >
          Crear pagina
        </button>

        {pages.length === 0 ? (
          <p>No hay paginas todavia</p>
        ) : (
          <ul>
            {pages.map((page) => (
              <ListItem
                key={page.id}
                title={page.title}
                orderText={`Posicion ${page.sort_order} de ${totalItems}`}
                secondaryText={
                  page.last_viewed_at
                    ? new Date(page.last_viewed_at).toLocaleString("es-AR")
                    : "Nunca"
                }
                variant="list"
                onClick={() =>
                  navigate(
                    `/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}`
                  )
                }
                onEdit={() =>
                  navigate(
                    `/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}/edit`
                  )
                }
                onMoveUp={() => handleStepMove(page, -1)}
                onMoveDown={() => handleStepMove(page, 1)}
                onMoveTo={() => setPageToMove(page)}
                disableMoveUp={page.sort_order <= 1}
                disableMoveDown={page.sort_order >= totalItems}
                isReordering={movingPageIds.includes(page.id)}
                onDelete={() => {
                  if (window.confirm("Eliminar esta pagina?")) {
                    handleDelete(page.id);
                  }
                }}
              />
            ))}
          </ul>
        )}

        <PaginationFooter
          currentPage={currentPage}
          hasPreviousPage={hasPreviousPage}
          hasNextPage={hasNextPage}
          onPreviousPage={() => goToPage(currentPage - 1)}
          onNextPage={() => goToPage(currentPage + 1)}
          onBack={() => navigate(`/subjects/${subject_id}`)}
          backLabel="Volver a temas"
        />
      </div>

      <ReorderModal
        currentPosition={pageToMove?.sort_order ?? 1}
        isOpen={Boolean(pageToMove)}
        itemId={pageToMove?.id ?? "page"}
        itemLabel={pageToMove?.title ?? ""}
        key={pageToMove?.id ?? "page-modal"}
        maxPosition={totalItems}
        onClose={() => setPageToMove(null)}
        onConfirm={confirmMoveTo}
      />
    </div>
  );
}

export default PagesPage;
