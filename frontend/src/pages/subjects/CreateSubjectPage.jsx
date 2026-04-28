import { useNavigate } from "react-router-dom";
import SubjectForm from "../../components/SubjectForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import SectionHeader from "../../components/SectionHeader";

function CreateSubjectPage() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const handleCreate = async (data) => {
    try {
      await fetchWithAuth("/subjects", token, {
        method: "POST",
        body: JSON.stringify(data),
      });

      navigate("/subjects");
    } catch (err) {
      console.error(err);
      alert("Error al crear");
    }
  };

  return (
    <div className="form-page">
      <SectionHeader
        title="Crear materia"
        subtitle="Definí una base clara para empezar a ordenar tus temas."
      />

      <SubjectForm
        buttonText="Crear"
        onSubmit={handleCreate}
        onCancel={() => navigate("/subjects")}
      />
    </div>
  );
}

export default CreateSubjectPage;
