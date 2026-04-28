import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";

function PagesPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPages = async () => {
      try {
        await fetchWithAuth(`/subjects/${subject_id}/topics/${topic_id}`, token);

        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}/pages`,
          token
        );
        setPages(data.items || []);
      } catch (err) {
        console.error(err);
        alert("Error al cargar paginas");
      } finally {
        setLoading(false);
      }
    };

    fetchPages();
  }, [subject_id, topic_id, token]);

  const deletePage = async (page_id) => {
    if (!window.confirm("Eliminar esta pagina?")) return;

    try {
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
        token,
        {
          method: "DELETE",
        }
      );

      setPages((prev) => prev.filter((p) => p.id !== page_id));
    } catch (err) {
      console.error(err);
      alert("Error al eliminar pagina");
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
            {pages.map((p) => (
              <ListItem
                key={p.id}
                title={p.title}
                secondaryText={`${
                  p.last_viewed_at
                    ? new Date(p.last_viewed_at).toLocaleString("es-AR")
                    : "Nunca"
                }`}
                variant="list"
                onClick={() =>
                  navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${p.id}`)
                }
                onEdit={() =>
                  navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${p.id}/edit`)
                }
                onDelete={() => deletePage(p.id)}
              />
            ))}
          </ul>
        )}

        <button onClick={() => navigate(`/subjects/${subject_id}`)}>
          Volver a temas
        </button>
      </div>
    </div>
  );
}

export default PagesPage;
