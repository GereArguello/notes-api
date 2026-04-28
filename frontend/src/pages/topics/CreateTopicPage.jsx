import { useNavigate, useParams } from "react-router-dom";
import TopicForm from "../../components/TopicForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import SectionHeader from "../../components/SectionHeader";

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
    <div className="form-page">
      <SectionHeader
        title="Crear tema"
        subtitle="Sumá una nueva sección para seguir separando ideas."
      />

      <TopicForm
        buttonText="Crear"
        onSubmit={handleCreate}
        onCancel={() => navigate(`/subjects/${subject_id}`)}
      />
    </div>
  );
}

export default CreateTopicPage;
