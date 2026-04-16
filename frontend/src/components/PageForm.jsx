import { useState, useEffect } from "react";

function PageForm({ initialData, onSubmit, buttonText, onCancel }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);

  // 🔹 cargar datos si estamos editando
  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || "");
      setContent(initialData.content || "");
    }
  }, [initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      title,
      content,
    }).catch(() => {
      setError("Error al guardar");
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{buttonText}</h2>

      <input
        type="text"
        placeholder="Título"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      <textarea
        placeholder="Contenido"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={15}
      />

      <button type="submit">{buttonText}</button>

      <button type="button" onClick={onCancel}>
        Cancelar
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}

export default PageForm;