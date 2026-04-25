function ListItem({
  title,
  subtitle,
  secondaryText,
  onClick,
  onEdit,
  onDelete,
}) {
  return (
    <li>
      <div onClick={onClick}>

        <div>
          <span>
            <strong>{title}</strong>
            {subtitle && ` — ${subtitle}`}
          </span>

          <span>
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
          </span>
        </div>

        <div>
          {secondaryText}
        </div>

      </div>
    </li>
  );
}

export default ListItem;