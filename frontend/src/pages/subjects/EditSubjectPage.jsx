import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import SubjectForm from "../../components/SubjectForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function EditSubjectPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [subject, setSubject] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔹 traer datos del subject
  useEffect(() => {
    const fetchSubject = async () => {
      try {
        const data = await fetchWithAuth(`/subjects/${id}`, token);
        setSubject(data);
      } catch (err) {
        console.error(err);
        alert("Error al cargar materia");
        navigate("/subjects");
      } finally {
        setLoading(false);
      }
    };

    fetchSubject();
  }, [id, token, navigate]);

  const handleUpdate = async (data) => {
    try {
      await fetchWithAuth(`/subjects/${id}`, token, {
        method: "PATCH",
        body: JSON.stringify(data),
      });

      navigate("/subjects");
    } catch (err) {
      console.error(err);
      alert("Error al actualizar");
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Editar materia</h1>

      <SubjectForm
        initialData={subject}
        buttonText="Guardar cambios"
        onSubmit={handleUpdate}
        onCancel={() => navigate("/subjects")}
      />
    </div>
  );
}

export default EditSubjectPage;