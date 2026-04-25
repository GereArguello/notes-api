import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import ListItem from "../../components/ListItem";

function PagesPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPages = async () => {
      try {
        //  esto actualiza last_viewed_at
        await fetchWithAuth(`/subjects/${subject_id}/topics/${topic_id}`, token);

        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}/pages`,
          token
        );
        setPages(data.items || []);
      } catch (err) {
        console.error(err);
        alert("Error al cargar páginas");
      } finally {
        setLoading(false);
      }
    };

    fetchPages();
  }, [subject_id, topic_id, token]);

  const deletePage = async (page_id) => {
    if (!window.confirm("¿Eliminar esta página?")) return;

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
      alert("Error al eliminar página");
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Páginas</h1>

      <button
        onClick={() =>
          navigate(
            `/subjects/${subject_id}/topics/${topic_id}/pages/new`
          )
        }
      >
        Crear página
      </button>

      {pages.length === 0 ? (
        <p>No hay páginas todavía</p>
      ) : (
      <ul>
        {pages.map((p) => (
          <ListItem
            key={p.id}
            title={p.title}
            secondaryText={`Última vez visto: ${
              p.last_viewed_at
                ? new Date(p.last_viewed_at).toLocaleString("es-AR")
                : "Nunca"
            }`}
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
  );
}

export default PagesPage;