import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TopicForm from "../components/TopicForm";

function EditTopicPage({ token }) {
  const { subject_id, topic_id } = useParams()
  const navigate = useNavigate();

  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔹 traer datos del topic
  useEffect(() => {
    fetch(`http://localhost:8000/subjects/${subject_id}/topics/${topic_id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        setTopic(data);
        setLoading(false);
      })
      .catch(() => {
        alert("Error al cargar tema");
        setLoading(false);
        navigate(`/subjects/${subject_id}`);
      });
  }, [subject_id, topic_id, token]);

  const handleUpdate = async (data) => {
    const res = await fetch(`http://localhost:8000/subjects/${subject_id}/topics/${topic_id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error("Error al actualizar");
    }

    navigate(`/subjects/${subject_id}`);
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Editar tema</h1>

      <TopicForm
        initialData={topic}
        buttonText="Guardar cambios"
        onSubmit={handleUpdate}
        onCancel={() => navigate(`/subjects/${subject_id}`)}
      />
    </div>
  );
}

export default EditTopicPage;