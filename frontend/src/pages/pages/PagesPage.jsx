import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function PagesPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
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
          <li key={p.id}>
            <div
              onClick={() =>
                navigate(
                  `/subjects/${subject_id}/topics/${topic_id}/pages/${p.id}`
                )
              }
            >
              {/*  fila principal */}
              <div>
                <span>
                  <strong>{p.title}</strong>
                </span>

                <span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(
                        `/subjects/${subject_id}/topics/${topic_id}/pages/${p.id}/edit`,
                        { state: { from: location.pathname } }
                      );
                    }}
                  >
                    Editar
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePage(p.id);
                    }}
                  >
                    Eliminar
                  </button>
                </span>
              </div>

              {/*  info secundaria */}
              <div>
                Última vez visto:{" "}
                {p.last_viewed_at
                  ? new Date(p.last_viewed_at).toLocaleString("es-AR")
                  : "Nunca"}
              </div>
            </div>
          </li>
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