import { useNavigate, useParams } from "react-router-dom";
import TopicForm from "../../components/TopicForm";
import { useAuth } from "../../context/AuthContext";

function CreateTopicPage() {
  const navigate = useNavigate();
  const { subject_id } = useParams();
  const { token } = useAuth();

  const handleCreate = async (data) => {
    const res = await fetch(
      `http://localhost:8000/subjects/${subject_id}/topics`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );

    if (!res.ok) {
      throw new Error("Error al crear");
    }

    // volver al subject
    navigate(`/subjects/${subject_id}`);
  };

  return (
    <div>
      <h1>Crear tema</h1>

      <TopicForm
        buttonText="Crear"
        onSubmit={handleCreate}
        onCancel={() => navigate(`/subjects/${subject_id}`)}
      />
    </div>
  );
}

export default CreateTopicPage;