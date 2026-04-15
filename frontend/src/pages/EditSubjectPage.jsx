import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import SubjectForm from "../components/SubjectForm";

function EditSubjectPage({ token }) {
  const { id } = useParams();
  const navigate = useNavigate();

  const [subject, setSubject] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔹 traer datos del subject
  useEffect(() => {
    fetch(`http://localhost:8000/subjects/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        setSubject(data);
        setLoading(false);
      })
      .catch(() => {
        alert("Error al cargar materia");
        navigate("/subjects");
      });
  }, [id, token]);

  const handleUpdate = async (data) => {
    const res = await fetch(`http://localhost:8000/subjects/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error("Error al actualizar");
    }

    navigate("/subjects");
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