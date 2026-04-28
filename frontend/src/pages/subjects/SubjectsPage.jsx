import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";
import "./SubjectsPage.css";

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
    <div className="page-container">
      <SectionHeader
        title="Mis materias"
        subtitle="Organizá tus cursadas, accesos recientes y nuevos apuntes."
      />
      <div className="card-container">
        <button onClick={() => navigate("/subjects/new")}>
          Crear materia
        </button>

        <ul className="subjects-grid">
          {subjects.map((s) => (
            <ListItem
              key={s.id}
              title={s.name}
              subtitle={s.difficulty_label}
              description={s.description}
              secondaryText={
                s.last_viewed_at
                  ? new Date(s.last_viewed_at).toLocaleString("es-AR")
                  : "Nunca"
              }
              variant="grid"
              onClick={() => navigate(`/subjects/${s.id}`)}
              onEdit={() => navigate(`/subjects/${s.id}/edit`)}
              onDelete={() => deleteSubject(s.id)}
            />
          ))}
        </ul>

        <button onClick={logout}>
          Logout
        </button>
      </div>
    </div>
  );
}

export default SubjectsPage;
