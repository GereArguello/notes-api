import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import { usePaginatedResource } from "../../hooks/usePaginatedResource";

import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";
import PaginationFooter from "../../components/PaginationFooter";

import { getErrorMessage } from "../../utils/errorMessage";
import { showAlertOnce } from "../../utils/showAlertOnce";

function PagesPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const {
    items: pages,
    loading,
    currentPage,
    hasPreviousPage,
    hasNextPage,
    goToPage,
    handleDelete,
  } = usePaginatedResource({
    pageSize: 20,

    fetchDataFn: async (page) => {
      // mantiene tu lógica original (last_viewed_at del topic)
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}`,
        token
      );

      return fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages?page=${page}`,
        token
      );
    },

    deleteFn: (pageId) =>
      fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages/${pageId}`,
        token,
        { method: "DELETE" }
      ),

    deps: [token, subject_id, topic_id], // 🔥 clave
  });

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
            navigate(
              `/subjects/${subject_id}/topics/${topic_id}/pages/new`
            )
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
    </div>
  );
}

export default PagesPage;