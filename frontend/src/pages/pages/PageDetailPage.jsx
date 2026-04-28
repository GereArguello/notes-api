import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function PageDetailPage() {
  const { subject_id, topic_id, page_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useAuth();

  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPage = async () => {
      try {
        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
          token
        );
        setPage(data);
      } catch (err) {
        console.error(err);
        alert("Error al cargar página");
        navigate(`/subjects/${subject_id}/topics/${topic_id}`);
      } finally {
        setLoading(false);
      }
    };

    fetchPage();
  }, [subject_id, topic_id, page_id, token, navigate]);

  if (loading) return <p>Cargando...</p>;

  return (
    <div className="page-detail-shell">
      <article className="note-sheet">
        <header className="note-sheet-header">
          <p className="note-sheet-label">Apunte</p>
          <h1>{page.title}</h1>
        </header>

        <div className="note-sheet-body">
          {(page.content || "Sin contenido").split("\n").map((line, index) => (
            <p key={`${page.id}-line-${index}`} className="note-line">
              {line || "\u00A0"}
            </p>
          ))}
        </div>

        <footer className="note-sheet-actions">
          <button
            onClick={() =>
              navigate(`/subjects/${subject_id}/topics/${topic_id}`)
            }
          >
            Volver
          </button>

          <button
            onClick={() =>
              navigate(
                `/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}/edit`,
                { state: { from: location.pathname } }
              )
            }
          >
            Editar
          </button>
        </footer>
      </article>
    </div>
  );
}

export default PageDetailPage;
