import { useState, useEffect } from "react";

function TopicForm({ initialData, onSubmit, buttonText, onCancel }) {
  const [name, setName] = useState("");
  const [error, setError] = useState(null);

  // 🔹 cargar datos si estamos editando
  useEffect(() => {
    if (initialData) {
      setName(initialData.name || "");
    }
  }, [initialData]);

    const handleSubmit = async (e) => {
    e.preventDefault();

    try {
        await onSubmit({ name });
    } catch {
        setError("Error al guardar");
    }
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

export default TopicForm;
