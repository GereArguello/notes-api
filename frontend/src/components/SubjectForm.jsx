import { useState, useEffect } from "react";

function SubjectForm({ initialData, onSubmit, buttonText, onCancel }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [difficulty, setDifficulty] = useState(1);
  const [error, setError] = useState(null);

  // 🔹 cargar datos si estamos editando
  useEffect(() => {
    if (initialData) {
      setName(initialData.name || "");
      setDescription(initialData.description || "");
      setDifficulty(initialData.difficulty || 1);
    }
  }, [initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      name,
      description,
      difficulty,
    }).catch(() => {
      setError("Error al guardar");
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{buttonText}</h2>

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

      <button type="submit">{buttonText}</button>
      <button type="button" onClick={onCancel}>
        Cancelar
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}

export default SubjectForm;