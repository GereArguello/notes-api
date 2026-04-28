import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TopicForm from "../../components/TopicForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import SectionHeader from "../../components/SectionHeader";

function EditTopicPage() {
  const { subject_id, topic_id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔹 traer datos del topic
  useEffect(() => {
    const fetchTopic = async () => {
      try {
        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}`,
          token
        );
        setTopic(data);
      } catch (err) {
        console.error(err);
        alert("Error al cargar tema");
        navigate(`/subjects/${subject_id}`);
      } finally {
        setLoading(false);
      }
    };

    fetchTopic();
  }, [subject_id, topic_id, token, navigate]);

  const handleUpdate = async (data) => {
    try {
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}`,
        token,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        }
      );

      navigate(`/subjects/${subject_id}`);
    } catch (err) {
      console.error(err);
      alert("Error al actualizar");
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div className="form-page">
      <SectionHeader
        title="Editar tema"
        subtitle="Reordená el foco del tema antes de seguir agregando páginas."
      />

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
