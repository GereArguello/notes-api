import { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import PageForm from "../../components/PageForm";

function EditPagePage({ token }) {
  const { subject_id, topic_id, page_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  const goBack = () => {
  if (location.state?.from) {
      navigate(location.state.from);
  } else {
      navigate(`/subjects/${subject_id}/topics/${topic_id}`);
  }
  };

  // 🔹 traer página
  useEffect(() => {
    fetch(
      `http://localhost:8000/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        setPage(data);
        setLoading(false);
      })
      .catch(() => {
        alert("Error al cargar página");
        navigate(`/subjects/${subject_id}/topics/${topic_id}`);
      });
  }, [subject_id, topic_id, page_id, token]);

  const handleUpdate = async (data) => {
    const res = await fetch(
      `http://localhost:8000/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );

    if (!res.ok) {
      throw new Error("Error al actualizar");
    }

    goBack();
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Editar página</h1>

      <PageForm
        initialData={page}
        buttonText="Guardar cambios"
        onSubmit={handleUpdate}
        onCancel={goBack}
      />
    </div>
  );
}

export default EditPagePage;