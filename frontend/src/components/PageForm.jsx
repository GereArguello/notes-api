import { useEffect, useState } from "react";
import PageSheet from "./PageSheet";

function PageForm({ initialData, onSubmit, buttonText, onCancel }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || "");
      setContent(initialData.content || "");
    }
  }, [initialData]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    try {
      await onSubmit({
        title,
        content,
      });
    } catch {
      setError("Error al guardar");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="page-detail-shell">
      <PageSheet
        title={title}
        content={content}
        isEditing
        onTitleChange={setTitle}
        onContentChange={setContent}
        actions={
          <>
            <button type="button" onClick={onCancel}>
              Cancelar
            </button>
            <button type="submit">{buttonText}</button>
          </>
        }
      />

      {error ? <p className="form-error page-form-error">{error}</p> : null}
    </form>
  );
}

export default PageForm;
