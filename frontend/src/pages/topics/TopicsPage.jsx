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

function TopicsPage() {
  const { subject_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const reorderResetTimeoutRef = useRef(null);
  const [movingTopicIds, setMovingTopicIds] = useState([]);
  const [topicToMove, setTopicToMove] = useState(null);

  const fetchTopics = useCallback(
    async (page) => {
      await fetchWithAuth(`/subjects/${subject_id}`, token);

      return fetchWithAuth(
        `/subjects/${subject_id}/topics?page=${page}`,
        token
      );
    },
    [subject_id, token]
  );

  const deleteTopic = useCallback(
    (topicId) =>
      fetchWithAuth(`/subjects/${subject_id}/topics/${topicId}`, token, {
        method: "DELETE",
      }),
    [subject_id, token]
  );

  const {
    items: topics,
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
    fetchDataFn: fetchTopics,
    deleteFn: deleteTopic,
  });

  const reorderTopic = async (topicId, sortOrder) => {
    await fetchWithAuth(
      `/subjects/${subject_id}/topics/${topicId}/re-order`,
      token,
      {
        method: "PATCH",
        body: JSON.stringify({ sort_order: sortOrder }),
      }
    );

    await refetch();
  };

  const pulseMovingTopics = (...ids) => {
    if (reorderResetTimeoutRef.current) {
      window.clearTimeout(reorderResetTimeoutRef.current);
    }

    setMovingTopicIds(ids);
    reorderResetTimeoutRef.current = window.setTimeout(() => {
      setMovingTopicIds([]);
    }, 260);
  };

  const handleStepMove = async (topic, direction) => {
    const nextSortOrder = topic.sort_order + direction;

    if (nextSortOrder < 1 || nextSortOrder > totalItems) {
      return;
    }

    const currentIndex = topics.findIndex((item) => item.id === topic.id);
    const swapIndex = currentIndex + direction;
    const swapTarget = topics[swapIndex];

    if (swapTarget && swapTarget.sort_order === nextSortOrder) {
      const previousTopics = topics;
      const reorderedTopics = [...topics];

      reorderedTopics[currentIndex] = {
        ...swapTarget,
        sort_order: topic.sort_order,
      };
      reorderedTopics[swapIndex] = {
        ...topic,
        sort_order: nextSortOrder,
      };

      updateItems(reorderedTopics);
      pulseMovingTopics(topic.id, swapTarget.id);

      try {
        await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic.id}/re-order`,
          token,
          {
            method: "PATCH",
            body: JSON.stringify({ sort_order: nextSortOrder }),
          }
        );
      } catch (error) {
        updateItems(previousTopics);
        setMovingTopicIds([]);
        showAlertOnce(getErrorMessage(error, "No se pudo reordenar el tema"));
      }

      return;
    }

    try {
      await reorderTopic(topic.id, nextSortOrder);
    } catch (error) {
      showAlertOnce(getErrorMessage(error, "No se pudo reordenar el tema"));
    }
  };

  const confirmMoveTo = async (nextSortOrder) => {
    if (!topicToMove) return;

    if (!Number.isInteger(nextSortOrder)) {
      showAlertOnce("Ingresa un numero entero valido.");
      return;
    }

    if (nextSortOrder < 1 || nextSortOrder > totalItems) {
      showAlertOnce(`La posicion debe estar entre 1 y ${totalItems}.`);
      return;
    }

    if (nextSortOrder === topicToMove.sort_order) {
      setTopicToMove(null);
      return;
    }

    try {
      await reorderTopic(topicToMove.id, nextSortOrder);
      setTopicToMove(null);
    } catch (error) {
      showAlertOnce(getErrorMessage(error, "No se pudo reordenar el tema"));
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div className="page-container">
      <SectionHeader
        title="Temas"
        subtitle="Entra a cada bloque para seguir construyendo tus apuntes."
      />

      <div className="list-container">
        <button
          type="button"
          onClick={() => navigate(`/subjects/${subject_id}/topics/new`)}
        >
          Crear tema
        </button>

        <ul>
          {topics.map((topic) => (
            <ListItem
              key={topic.id}
              title={topic.name}
              orderText={`Posicion ${topic.sort_order} de ${totalItems}`}
              secondaryText={
                topic.last_viewed_at
                  ? new Date(topic.last_viewed_at).toLocaleString("es-AR")
                  : "Nunca"
              }
              variant="list"
              onClick={() =>
                navigate(`/subjects/${subject_id}/topics/${topic.id}`)
              }
              onEdit={() =>
                navigate(`/subjects/${subject_id}/topics/${topic.id}/edit`)
              }
              onMoveUp={() => handleStepMove(topic, -1)}
              onMoveDown={() => handleStepMove(topic, 1)}
              onMoveTo={() => setTopicToMove(topic)}
              disableMoveUp={topic.sort_order <= 1}
              disableMoveDown={topic.sort_order >= totalItems}
              isReordering={movingTopicIds.includes(topic.id)}
              onDelete={() => {
                if (window.confirm("Seguro que queres eliminar este tema?")) {
                  handleDelete(topic.id);
                }
              }}
            />
          ))}
        </ul>

        <PaginationFooter
          currentPage={currentPage}
          hasPreviousPage={hasPreviousPage}
          hasNextPage={hasNextPage}
          onPreviousPage={() => goToPage(currentPage - 1)}
          onNextPage={() => goToPage(currentPage + 1)}
          onBack={() => navigate("/subjects")}
          backLabel="Volver atras"
        />
      </div>

      <ReorderModal
        currentPosition={topicToMove?.sort_order ?? 1}
        isOpen={Boolean(topicToMove)}
        itemId={topicToMove?.id ?? "topic"}
        itemLabel={topicToMove?.name ?? ""}
        key={topicToMove?.id ?? "topic-modal"}
        maxPosition={totalItems}
        onClose={() => setTopicToMove(null)}
        onConfirm={confirmMoveTo}
      />
    </div>
  );
}

export default TopicsPage;
