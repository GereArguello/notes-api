import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import { getErrorMessage } from "../../utils/errorMessage";
import { showAlertOnce } from "../../utils/showAlertOnce";
import PageSheet from "../../components/PageSheet";

function PageDetailPage() {
  const { subject_id, topic_id, page_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useAuth();

  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

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
        showAlertOnce(getErrorMessage(err, "Error al cargar la pagina"));
        navigate(`/subjects/${subject_id}/topics/${topic_id}`);
      } finally {
        setLoading(false);
      }
    };

    fetchPage();
  }, [subject_id, topic_id, page_id, token, navigate]);

  if (loading) return <p>Cargando...</p>;

  return (
    <div className="page-detail-shell">
      <PageSheet
        title={page.title}
        content={page.content}
        actions={
          <>
            <button
              onClick={() =>
                navigate(`/subjects/${subject_id}/topics/${topic_id}`)
              }
            >
              Volver
            </button>

            <button
              onClick={() =>
                navigate(
                  `/subjects/${subject_id}/topics/${topic_id}/pages/${page.id}/edit`,
                  { state: { from: location.pathname } }
                )
              }
            >
              Editar
            </button>
          </>
        }
      />
    </div>
  );
}

export default PageDetailPage;
