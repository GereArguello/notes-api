import { useNavigate, useParams } from "react-router-dom";
import PageForm from "../../components/PageForm";
import { useAuth } from "../../context/AuthContext";

function CreatePagePage() {
  const navigate = useNavigate();
  const { subject_id, topic_id } = useParams();
  const { token } = useAuth();

  const handleCreate = async (data) => {
    const res = await fetch(
      `http://localhost:8000/subjects/${subject_id}/topics/${topic_id}/pages`,
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
      throw new Error("Error al crear página");
    }

    navigate(`/subjects/${subject_id}/topics/${topic_id}`);
  };

  return (
    <div>
      <h1>Crear página</h1>

      <PageForm
        buttonText="Crear"
        onSubmit={handleCreate}
        onCancel={() =>
          navigate(`/subjects/${subject_id}/topics/${topic_id}`)
        }
      />
    </div>
  );
}

export default CreatePagePage;