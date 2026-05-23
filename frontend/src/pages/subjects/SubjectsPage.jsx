import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { fetchWithAuth } from "../../api/fetchWithAuth";
import { usePaginatedResource } from "../../hooks/usePaginatedResource";

import ListItem from "../../components/ListItem";
import SectionHeader from "../../components/SectionHeader";
import PaginationFooter from "../../components/PaginationFooter";

import "./SubjectsPage.css";

function SubjectsPage() {
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const fetchSubjects = useCallback(
    (page) => fetchWithAuth(`/subjects?page=${page}&size=9`, token),
    [token]
  );

  const deleteSubject = useCallback(
    (id) =>
      fetchWithAuth(`/subjects/${id}`, token, {
        method: "DELETE",
      }),
    [token]
  );

  const {
    items: subjects,
    loading,
    currentPage,
    hasPreviousPage,
    hasNextPage,
    goToPage,
    handleDelete,
  } = usePaginatedResource({
    pageSize: 9,
    fetchDataFn: fetchSubjects,
    deleteFn: deleteSubject,
  });

  if (loading) return <p>Cargando...</p>;

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
              onDelete={() => handleDelete(s.id)}
            />
          ))}
        </ul>

        <PaginationFooter
          currentPage={currentPage}
          hasPreviousPage={hasPreviousPage}
          hasNextPage={hasNextPage}
          onPreviousPage={() => goToPage(currentPage - 1)}
          onNextPage={() => goToPage(currentPage + 1)}
          onBack={logout}
          backLabel="Cerrar sesión"
        />
      </div>
    </div>
  );
}

export default SubjectsPage;
