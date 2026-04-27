import "./ListItem.css";

function ListItem({
  title,
  subtitle,
  secondaryText,
  description,
  onClick,
  onEdit,
  onDelete,
  variant = "list",
}) {
  const desc = description || "Sin descripción";

  //  LIST (filas)
  if (variant === "list") {
    return (
      <li className="list-item list-item-list" onClick={onClick}>
        
        {/* 🔹 columna 1 */}
        <div className="list-item-main">
          <div className="list-item-title">
            <strong>{title}</strong>
          </div>
        </div>

        {/* 🔹 columna 2 */}
        <div className="list-item-secondary">
          <div className="list-item-secondary-label">
            Última vez visto
          </div>
          <div className="list-item-secondary-date">
            {secondaryText}
          </div>
        </div>

        {/* 🔹 columna 3 */}
        <div className="list-item-actions">
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
            >
              Editar
            </button>
          )}

          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
            >
              Eliminar
            </button>
          )}
        </div>

      </li>
    );
  }

  //  GRID (materias) 
  return (
    <li className="list-item list-item-grid" onClick={onClick}>
      
      <div className="list-item-content">
        <div className="list-item-title">
          <strong>{title}</strong>
        </div>

        {subtitle && (
          <div className="list-item-subtitle">
            {subtitle}
          </div>
        )}

        <div className="list-item-description-wrapper">
          <div className="list-item-description">
            {desc}
          </div>

          <div className="list-item-tooltip">
            {desc}
          </div>
        </div>

        <div className="list-item-secondary">
          <div className="list-item-secondary-label">
            Última vez visto
          </div>
          <div className="list-item-secondary-date">
            {secondaryText}
          </div>
        </div>
      </div>

      <div className="list-item-actions">
        {onEdit && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
            }}
          >
            Editar
          </button>
        )}

        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
          >
            Eliminar
          </button>
        )}
      </div>

    </li>
  );
}

export default ListItem;