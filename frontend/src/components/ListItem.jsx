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
  return (
    <li className={`list-item list-item-${variant}`} onClick={onClick}>
    
    {/* 🔹 contenido */}
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

    {/* 🔹 acciones */}
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