import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import { usePaginatedResource } from "../../hooks/usePaginatedResource";

import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";
import PaginationFooter from "../../components/PaginationFooter";

function TopicsPage() {
  const { subject_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const {
    items: topics,
    loading,
    currentPage,
    hasPreviousPage,
    hasNextPage,
    goToPage,
    handleDelete,
  } = usePaginatedResource({
    pageSize: 20,

    fetchDataFn: async (page) => {
      // 👇 esto mantiene tu lógica original (update last_viewed_at)
      await fetchWithAuth(`/subjects/${subject_id}`, token);

      return fetchWithAuth(
        `/subjects/${subject_id}/topics?page=${page}`,
        token
      );
    },

    deleteFn: (topicId) =>
      fetchWithAuth(
        `/subjects/${subject_id}/topics/${topicId}`,
        token,
        { method: "DELETE" }
      ),

    deps: [token, subject_id], // 🔥 clave
  });

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
          onClick={() =>
            navigate(`/subjects/${subject_id}/topics/new`)
          }
        >
          Crear tema
        </button>

        <ul>
          {topics.map((topic) => (
            <ListItem
              key={topic.id}
              title={topic.name}
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
    </div>
  );
}

export default TopicsPage;