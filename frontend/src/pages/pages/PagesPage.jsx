import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";
import PaginationFooter from "../../components/PaginationFooter";
import { getErrorMessage } from "../../utils/errorMessage";
import { showAlertOnce } from "../../utils/showAlertOnce";

function PagesPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { token } = useAuth();

  const [pages, setPages] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
  });
  const [loading, setLoading] = useState(true);

  const currentPage = Math.max(1, Number(searchParams.get("page")) || 1);
  const totalPages = Math.max(1, Math.ceil(pagination.total / pagination.size));
  const hasPreviousPage = currentPage > 1;
  const hasNextPage = currentPage < totalPages;

  const goToPage = (page) => {
    const nextPage = Math.max(1, page);
    const nextParams = new URLSearchParams(searchParams);

    if (nextPage === 1) {
      nextParams.delete("page");
    } else {
      nextParams.set("page", String(nextPage));
    }

    setSearchParams(nextParams);
  };

  useEffect(() => {
    const fetchPages = async () => {
      setLoading(true);

      try {
        await fetchWithAuth(`/subjects/${subject_id}/topics/${topic_id}`, token);

        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}/pages?page=${currentPage}`,
          token
        );

        const size = data.size || 20;
        const total = data.total || 0;
        const fetchedTotalPages = Math.max(1, Math.ceil(total / size));

        setPages(data.items || []);
        setPagination({
          page: data.page || currentPage,
          size,
          total,
        });

        if (currentPage > fetchedTotalPages) {
          goToPage(fetchedTotalPages);
        }
      } catch (err) {
        console.error(err);
        showAlertOnce(getErrorMessage(err, "Error al cargar paginas"));
      } finally {
        setLoading(false);
      }
    };

    fetchPages();
  }, [subject_id, topic_id, token, currentPage]);

  const deletePage = async (pageId) => {
    if (!window.confirm("Eliminar esta pagina?")) return;

    try {
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages/${pageId}`,
        token,
        {
          method: "DELETE",
        }
      );

      const remainingItems = pages.length - 1;
      const previousTotalPages = Math.max(
        1,
        Math.ceil((pagination.total - 1) / pagination.size)
      );

      if (remainingItems === 0 && currentPage > 1 && currentPage > previousTotalPages) {
        goToPage(currentPage - 1);
        return;
      }

      const data = await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages?page=${currentPage}`,
        token
      );

      setPages(data.items || []);
      setPagination({
        page: data.page || currentPage,
        size: data.size || pagination.size,
        total: data.total || 0,
      });
    } catch (err) {
      console.error(err);
      showAlertOnce(getErrorMessage(err, "Error al eliminar la pagina"));
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
          onClick={() => navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/new`)}
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
                secondaryText={`${
                  page.last_viewed_at
                    ? new Date(page.last_viewed_at).toLocaleString("es-AR")
                    : "Nunca"
                }`}
                variant="list"
                onClick={() =>
                  navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}`)
                }
                onEdit={() =>
                  navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}/edit`)
                }
                onDelete={() => deletePage(page.id)}
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
