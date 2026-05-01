import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";
import PaginationFooter from "../../components/PaginationFooter";

function TopicsPage() {
  const { subject_id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { token } = useAuth();

  const [topics, setTopics] = useState([]);
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
    const fetchTopics = async () => {
      setLoading(true);

      try {
        await fetchWithAuth(`/subjects/${subject_id}`, token);

        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics?page=${currentPage}`,
          token
        );

        const size = data.size || 20;
        const total = data.total || 0;
        const fetchedTotalPages = Math.max(1, Math.ceil(total / size));

        setTopics(data.items || []);
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
        alert("Error al cargar temas");
      } finally {
        setLoading(false);
      }
    };

    fetchTopics();
  }, [subject_id, token, currentPage]);

  const deleteTopic = async (topicId) => {
    const confirmDelete = window.confirm("Seguro que queres eliminar este tema?");
    if (!confirmDelete) return;

    try {
      await fetchWithAuth(`/subjects/${subject_id}/topics/${topicId}`, token, {
        method: "DELETE",
      });

      const remainingItems = topics.length - 1;
      const previousTotalPages = Math.max(
        1,
        Math.ceil((pagination.total - 1) / pagination.size)
      );

      if (remainingItems === 0 && currentPage > 1 && currentPage > previousTotalPages) {
        goToPage(currentPage - 1);
        return;
      }

      const data = await fetchWithAuth(
        `/subjects/${subject_id}/topics?page=${currentPage}`,
        token
      );

      setTopics(data.items || []);
      setPagination({
        page: data.page || currentPage,
        size: data.size || pagination.size,
        total: data.total || 0,
      });
    } catch (err) {
      console.error(err);
      alert("Error al eliminar el tema");
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
        <button type="button" onClick={() => navigate(`/subjects/${subject_id}/topics/new`)}>
          Crear tema
        </button>

        <ul>
          {topics.map((topic) => (
            <ListItem
              key={topic.id}
              title={topic.name}
              secondaryText={`${
                topic.last_viewed_at
                  ? new Date(topic.last_viewed_at).toLocaleString("es-AR")
                  : "Nunca"
              }`}
              variant="list"
              onClick={() => navigate(`/subjects/${subject_id}/topics/${topic.id}`)}
              onEdit={() => navigate(`/subjects/${subject_id}/topics/${topic.id}/edit`)}
              onDelete={() => deleteTopic(topic.id)}
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
