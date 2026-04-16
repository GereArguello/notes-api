import { useEffect, useState} from "react";
import { useParams, useNavigate, useLocation} from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

function PagesPage() {
    const { subject_id, topic_id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const { token } = useAuth();

    const [pages, setPages] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch(`http://localhost:8000/subjects/${subject_id}/topics/${topic_id}/pages`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        })
          .then((res) => {
            if (!res.ok) throw new Error();
            return res.json();
          })
          .then((data) => {
            setPages(data.items || []);
            setLoading(false);
          })
          .catch(() => {
            setLoading(false);
            alert("Error al cargar páginas")
          })
    }, [subject_id, topic_id, token])

    const deletePage = async (page_id) => {
    if (!window.confirm("¿Eliminar esta página?")) return;

    try {
        const res = await fetch(
        `http://localhost:8000/subjects/${subject_id}/topics/${topic_id}/pages/${page_id}`,
        {
            method: "DELETE",
            headers: {
            Authorization: `Bearer ${token}`,
            },
        }
        );

        if (!res.ok) throw new Error();

        setPages((prev) => prev.filter((p) => p.id !== page_id));

    } catch {
        alert("Error al eliminar página");
    }
    };

    if (loading) return <p>Cargando...</p>;

    return (
        <div>
            <h1>Páginas</h1>

            <button onClick={() => navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/new`)}>
                Crear página
            </button>

            {pages.length === 0 ? (
                <p>No hay páginas todavía</p>
            ) : (
            <ul>
                {pages.map((p) => (
                    <li key={p.id}>
                        {p.title}

                    <button
                    onClick={() =>
                        navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${p.id}/edit`,
                        {state: { from: location.pathname}}
                        )
                    }
                    >
                    Editar
                    </button>

                    <button onClick={() => deletePage(p.id)}>
                    Eliminar
                    </button>

                    <button
                    onClick={() =>
                        navigate(`/subjects/${subject_id}/topics/${topic_id}/pages/${p.id}`)
                    }
                    >
                    Ver
                    </button>
                    </li>
                ))}
            </ul>
            )}

            <button onClick={() => navigate(`/subjects/${subject_id}`)}>
            Volver a temas
            </button>

        </div>
    )
}

export default PagesPage;