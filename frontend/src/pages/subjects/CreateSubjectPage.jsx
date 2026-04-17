import { useNavigate } from "react-router-dom";
import SubjectForm from "../../components/SubjectForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

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
    <div>
      <h1>Crear materia</h1>

      <SubjectForm
        buttonText="Crear"
        onSubmit={handleCreate}
        onCancel={() => navigate("/subjects")}
      />
    </div>
  );
}

export default CreateSubjectPage;