import { useState } from "react";

function CreateSubjectForm({ token, onCreated }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [difficulty, setDifficulty] = useState(1);
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault(); // evita recargar la página

    fetch("http://localhost:8000/subjects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name,
        description,
        difficulty
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Error al crear materia");
        }
        return res.json();
      })
      .then((data) => {
        setName("");
        setDescription("");
        setDifficulty(1);
        setError(null);

        // avisar al padre (SubjectsPage) que se creó una materia
        onCreated(data);
      })
      .catch(() => {
        setError("No se pudo crear la materia");
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Crear materia</h2>

      <input
        type="text"
        placeholder="Nombre"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />

      <input
        type="text"
        placeholder="Descripción"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <select
        value={difficulty}
        onChange={(e) => setDifficulty(Number(e.target.value))}
      >
        <option value={1}>Muy fácil</option>
        <option value={2}>Fácil</option>
        <option value={3}>Media</option>
        <option value={4}>Difícil</option>
        <option value={5}>Muy difícil</option>
      </select>

      <button type="submit">Crear</button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}

export default CreateSubjectForm;