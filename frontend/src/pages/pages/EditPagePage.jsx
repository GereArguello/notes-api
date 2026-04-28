import { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import PageForm from "../../components/PageForm";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import SectionHeader from "../../components/SectionHeader";

function EditPagePage() {
  const { subject_id, topic_id, page_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useAuth();

  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  const goBack = () => {
    if (location.state?.from) {
      navigate(location.state.from);
    } else {
      navigate(`/subjects/${subject_id}/topics/${topic_id}`);
    }
  };

  useEffect(() => {
    const fetchPage = async () => {
      try {
        const data = await fetchWithAuth(
          `/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
          token
        );
        setPage(data);
      } catch (err) {
        console.error(err);
        alert("Error al cargar pagina");
        navigate(`/subjects/${subject_id}/topics/${topic_id}`);
      } finally {
        setLoading(false);
      }
    };

    fetchPage();
  }, [subject_id, topic_id, page_id, token, navigate]);

  const handleUpdate = async (data) => {
    try {
      await fetchWithAuth(
        `/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
        token,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        }
      );

      goBack();
    } catch (err) {
      console.error(err);
      alert("Error al actualizar");
    }
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div className="form-page">
      <SectionHeader
        title="Editar pagina"
        subtitle="Puli el contenido y mantene tus apuntes claros y legibles."
      />

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
