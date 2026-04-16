import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

function PageDetailPage() {
  const { subject_id, topic_id, page_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useAuth();

  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔹 traer página
  useEffect(() => {
    fetch(
      `http://localhost:8000/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        setPage(data);
        setLoading(false);
      })
      .catch(() => {
        alert("Error al cargar página");
        navigate(`/subjects/${subject_id}/topics/${topic_id}`);
      });
  }, [subject_id, topic_id, page_id, token]);

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>{page.title}</h1>

      <p>{page.content || "Sin contenido"}</p>

      <button
        onClick={() =>
          navigate(`/subjects/${subject_id}/topics/${topic_id}`)
        }
      >
        Volver
      </button>

      <button
      onClick={() =>
          navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}/edit`,
          {state: { from: location.pathname}}
          )
      }
      >
        Editar
      </button>
    </div>
  );
}

export default PageDetailPage;