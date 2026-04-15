import { useEffect, useState } from "react";
import CreateSubjectForm from "../components/CreateSubjectForm";

function SubjectsPage({ token, onLogout }) {
  const [subjects, setSubjects] = useState([]);

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

  const handleCreated = () => {
    fetchSubjects();
  };

  return (
    <div>
      <h1>Mis materias</h1>

      <CreateSubjectForm 
        token={token} 
        onCreated={handleCreated} 
      />

      <ul>
        {subjects.map((s) => (
          <li key={s.id}>
            <strong>{s.name}</strong> — {s.difficulty_label}
          </li>
        ))}
      </ul>

      <button onClick={onLogout}>
        Logout
      </button>
    </div>
  );
}

export default SubjectsPage;