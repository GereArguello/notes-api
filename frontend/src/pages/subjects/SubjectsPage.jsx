import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

function SubjectsPage() {
  const [subjects, setSubjects] = useState([]);
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const fetchSubjects = () => {
    fetch("http://localhost:8000/subjects", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (res.status === 401) {
          onLogout();
          return Promise.reject();
        }
        return res.json();
      })
      .then((data) => {
        if (data) {
          setSubjects(data.items);
        }
      });
  };

  useEffect(() => {
    fetchSubjects();
  }, [token]);

  const deleteSubject = (id) => {
    if (!window.confirm("¿Seguro que querés eliminar esta materia?")) return;

    fetch(`http://localhost:8000/subjects/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error();
        fetchSubjects();
      })
      .catch(() => {
        alert("Error al eliminar");
      });
  };

  return (
    <div>
      <h1>Mis materias</h1>

      {/* 🔹 botón crear */}
      <button onClick={() => navigate("/subjects/new")}>
         Crear materia
      </button>

      <ul>
        {subjects.map((s) => (
          <li key={s.id}>
            <strong>{s.name}</strong> — {s.difficulty_label}

            {/* 🔹 editar */}
            <button onClick={() => navigate(`/subjects/${s.id}/edit`)}>
              Editar
            </button>

            {/* 🔹 eliminar */}
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