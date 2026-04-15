import { useNavigate } from "react-router-dom";
import SubjectForm from "../../components/SubjectForm";

function CreateSubjectPage({ token }) {
  const navigate = useNavigate();

  const handleCreate = async (data) => {
    const res = await fetch("http://localhost:8000/subjects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error("Error al crear");
    }

    // volver al listado
    navigate("/subjects");
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