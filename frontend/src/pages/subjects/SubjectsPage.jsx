import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";

function SubjectsPage() {
  const [subjects, setSubjects] = useState([]);
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const fetchSubjects = async () => {
    try {
      const data = await fetchWithAuth("/subjects", token);
      setSubjects(data.items);
    } catch (err) {
      console.error(err);
      alert("Error al cargar materias");
    }
  };

  useEffect(() => {
    fetchSubjects();
  }, [token]);

  const deleteSubject = async (id) => {
    if (!window.confirm("¿Seguro que querés eliminar esta materia?")) return;

    try {
      await fetchWithAuth(`/subjects/${id}`, token, {
        method: "DELETE",
      });

      fetchSubjects(); // refrescar lista
    } catch (err) {
      console.error(err);
      alert("Error al eliminar");
    }
  };

  return (
    <div>
      <h1>Mis materias</h1>

      <button onClick={() => navigate("/subjects/new")}>
        Crear materia
      </button>

      <ul>
        {subjects.map((s) => (
          <li key={s.id}>
            <strong>{s.name}</strong> — {s.difficulty_label}

            <button onClick={() => navigate(`/subjects/${s.id}/edit`)}>
              Editar
            </button>

            <button onClick={() => deleteSubject(s.id)}>
              Eliminar
            </button>

            <button onClick={() => navigate(`/subjects/${s.id}`)}>
              Ver
            </button>
          </li>
        ))}
      </ul>

      <button onClick={logout}>
        Logout
      </button>
    </div>
  );
}

export default SubjectsPage;