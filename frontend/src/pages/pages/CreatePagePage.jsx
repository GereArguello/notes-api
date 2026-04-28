import { useNavigate, useParams } from "react-router-dom";
import PageForm from "../../components/PageForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import SectionHeader from "../../components/SectionHeader";
import { getErrorMessage } from "../../utils/errorMessage";
import { showAlertOnce } from "../../utils/showAlertOnce";

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
      showAlertOnce(getErrorMessage(err, "Error al crear la pagina"));
    }
  };

  return (
    <div className="form-page">
      <SectionHeader
        title="Crear pagina"
        subtitle="Abri una hoja nueva para volcar ideas, clases y resumenes."
      />

      <PageForm
        buttonText="Crear"
        onSubmit={handleCreate}
        onCancel={() => navigate(`/subjects/${subject_id}/topics/${topic_id}`)}
      />
    </div>
  );
}

export default CreatePagePage;
