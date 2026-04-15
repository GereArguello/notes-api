import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

function TopicsPage({ token }) {
  const { subject_id } = useParams();
  const navigate = useNavigate();

  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🔹 traer topics
  useEffect(() => {
    fetch(`http://localhost:8000/subjects/${subject_id}/topics`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        setTopics(data.items);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
        alert("Error al cargar temas");
      });
  }, [subject_id, token]);

  // 🔹 eliminar topic
  const deleteTopic = async (topic_id) => {
    const confirmDelete = window.confirm("¿Seguro que querés eliminar este tema?");
    if (!confirmDelete) return;

    try {
      const res = await fetch(
        `http://localhost:8000/subjects/${subject_id}/topics/${topic_id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        throw new Error();
      }

      // ✅ actualizar estado local (sin refetch)
      setTopics((prev) => prev.filter((t) => t.id !== topic_id));

    } catch {
      alert("Error al eliminar el tema");
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Temas</h1>

      <button onClick={() => navigate(`/subjects/${subject_id}/topics/new`)}>
        + Crear tema
      </button>

      <ul>
        {topics.map((t) => (
          <li key={t.id}>
            {t.name}

            <button
              onClick={() =>
                navigate(`/subjects/${subject_id}/topics/${t.id}/edit`)
              }
            >
              Editar
            </button>

            <button onClick={() => deleteTopic(t.id)}>
              Eliminar
            </button>

            <button
              onClick={() =>
                navigate(`/subjects/${subject_id}/topics/${t.id}`)
              }
            >
              Ver
            </button>
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