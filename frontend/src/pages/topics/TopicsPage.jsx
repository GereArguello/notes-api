import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function TopicsPage() {
  const { subject_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopic = async () => {
      try {
        //  esto actualiza last_viewed_at
        await fetchWithAuth(`/subjects/${subject_id}`, token);

        //  esto trae los topics
        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics`,
          token
        );

        setTopics(data.items);
      } catch (err) {
        console.error(err);
        alert("Error al cargar temas");
      } finally {
        setLoading(false);
      }
    };

    fetchTopic();
  }, [subject_id, token]);

  // 🔹 eliminar topic
  const deleteTopic = async (topic_id) => {
    const confirmDelete = window.confirm("¿Seguro que querés eliminar este tema?");
    if (!confirmDelete) return;

    try {
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}`,
        token,
        {
          method: "DELETE",
        }
      );

      // ✅ mantener tu optimización (sin refetch)
      setTopics((prev) => prev.filter((t) => t.id !== topic_id));

    } catch (err) {
      console.error(err);
      alert("Error al eliminar el tema");
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Temas</h1>

      <button onClick={() => navigate(`/subjects/${subject_id}/topics/new`)}>
         Crear tema
      </button>

      <ul>
        {topics.map((t) => (
          <li key={t.id}>
            <div
              onClick={() =>
                navigate(`/subjects/${subject_id}/topics/${t.id}`)
              }
            >
              {/*  fila principal */}
              <div>
                <span>
                  <strong>{t.name}</strong>
                </span>

                <span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(
                        `/subjects/${subject_id}/topics/${t.id}/edit`
                      );
                    }}
                  >
                    Editar
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteTopic(t.id);
                    }}
                  >
                    Eliminar
                  </button>
                </span>
              </div>

              {/*  info secundaria */}
              <div>
                Última vez visto:{" "}
                {t.last_viewed_at
                  ? new Date(t.last_viewed_at).toLocaleString("es-AR")
                  : "Nunca"}
              </div>
            </div>
          </li>
        ))}
      </ul>

      <button onClick={() => navigate(`/subjects`)}>
        Volver atrás
      </button>
    </div>
  );
}

export default TopicsPage;