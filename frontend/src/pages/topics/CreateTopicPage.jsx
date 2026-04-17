import { useNavigate, useParams } from "react-router-dom";
import TopicForm from "../../components/TopicForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function CreateTopicPage() {
  const navigate = useNavigate();
  const { subject_id } = useParams();
  const { token } = useAuth();

  const handleCreate = async (data) => {
    try{
      await fetchWithAuth(
        `/subjects/${subject_id}/topics`, token, {
          method: "POST",
          body: JSON.stringify(data),
        });
        navigate(`/subjects/${subject_id}`);
    } catch(err) {
      console.error(err);
      alert("Error al crear")
    }
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