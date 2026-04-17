import { useNavigate, useParams } from "react-router-dom";
import PageForm from "../../components/PageForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function CreatePagePage() {
  const navigate = useNavigate();
  const { subject_id, topic_id } = useParams();
  const { token } = useAuth();

  const handleCreate = async (data) => {
    try {
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages`,
        token,
        {
          method: "POST",
          body: JSON.stringify(data),
        }
      );

      navigate(`/subjects/${subject_id}/topics/${topic_id}`);
    } catch (err) {
      console.error(err);
      alert("Error al crear página");
    }
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