import { useState } from "react";

function SubjectForm({ initialData, onSubmit, buttonText, onCancel }) {
  const [name, setName] = useState(() => initialData?.name || "");
  const [description, setDescription] = useState(
    () => initialData?.description || ""
  );
  const [difficulty, setDifficulty] = useState(
    () => initialData?.difficulty || 1
  );
  const [error, setError] = useState(null);

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
    <form onSubmit={handleSubmit} className="entity-form">
      <h2>{buttonText}</h2>

      <input
        type="text"
        placeholder="Nombre"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />

      <textarea
        placeholder="Descripcion"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={4}
      />

      <label className="field-group">
        <span>Dificultad</span>
        <select
          value={difficulty}
          onChange={(e) => setDifficulty(Number(e.target.value))}
        >
          <option value={1}>Muy facil</option>
          <option value={2}>Facil</option>
          <option value={3}>Media</option>
          <option value={4}>Dificil</option>
          <option value={5}>Muy dificil</option>
        </select>
      </label>

      <div className="form-actions">
        <button type="submit">{buttonText}</button>
        <button type="button" onClick={onCancel}>
          Cancelar
        </button>
      </div>

      {error && <p className="form-error">{error}</p>}
    </form>
  );
}

export default SubjectForm;
