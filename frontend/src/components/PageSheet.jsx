function PageSheet({
  title = "",
  content = "",
  isEditing = false,
  onTitleChange,
  onContentChange,
  actions,
}) {
  return (
    <article className="note-sheet">
      <header className="note-sheet-header">
        <p className="note-sheet-label">Apunte</p>
        {isEditing ? (
          <input
            type="text"
            className="note-title-input"
            placeholder="Titulo"
            value={title}
            onChange={(event) => onTitleChange?.(event.target.value)}
            required
          />
        ) : (
          <h1>{title}</h1>
        )}
      </header>

      <div className="note-sheet-body">
        {isEditing ? (
          <textarea
            className="note-content-input"
            placeholder="Empeza a escribir tu apunte..."
            value={content}
            onChange={(event) => onContentChange?.(event.target.value)}
            rows={15}
          />
        ) : (
          (content || "Sin contenido").split("\n").map((line, index) => (
            <p key={`line-${index}`} className="note-line">
              {line || "\u00A0"}
            </p>
          ))
        )}
      </div>

      {actions ? <footer className="note-sheet-actions">{actions}</footer> : null}
    </article>
  );
}

export default PageSheet;
