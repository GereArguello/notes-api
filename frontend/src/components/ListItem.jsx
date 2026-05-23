import React, { useRef, useState } from "react";
import "./ListItem.css";

function ActionButton({
  ariaLabel,
  className = "",
  disabled = false,
  onClick,
  title,
  children,
}) {
  return (
    <button
      type="button"
      aria-label={ariaLabel}
      className={className}
      disabled={disabled}
      title={title}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    >
      {children}
    </button>
  );
}

function ListItem({
  title,
  subtitle,
  secondaryText,
  orderText,
  description,
  onClick,
  onEdit,
  onDelete,
  onMoveUp,
  onMoveDown,
  onMoveTo,
  disableMoveUp = false,
  disableMoveDown = false,
  isReordering = false,
  variant = "list",
}) {
  const desc = description;
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const timeoutRef = useRef(null);

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => setTooltipVisible(true), 1000);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setTooltipVisible(false);
  };

  const renderOrderMeta = () => (
    <div className="list-item-secondary">
      {orderText && <div className="list-item-order">{orderText}</div>}
      <div className="list-item-secondary-label">Ultima vez visto</div>
      <div className="list-item-secondary-date">{secondaryText}</div>
    </div>
  );

  const renderActions = () => (
    <div className="list-item-actions">
      {onEdit && <ActionButton onClick={onEdit}>Editar</ActionButton>}
      {onMoveUp && (
        <ActionButton
          ariaLabel="Subir una posicion"
          className="list-item-icon-button"
          disabled={disableMoveUp}
          onClick={onMoveUp}
          title="Subir"
        >
          ↑
        </ActionButton>
      )}
      {onMoveDown && (
        <ActionButton
          ariaLabel="Bajar una posicion"
          className="list-item-icon-button"
          disabled={disableMoveDown}
          onClick={onMoveDown}
          title="Bajar"
        >
          ↓
        </ActionButton>
      )}
      {onMoveTo && (
        <ActionButton
          ariaLabel="Mover a otra posicion"
          className="list-item-jump-button"
          onClick={onMoveTo}
          title="Mover a otra posicion"
        >
          Mover a...
        </ActionButton>
      )}
      {onDelete && <ActionButton onClick={onDelete}>Eliminar</ActionButton>}
    </div>
  );

  if (variant === "list") {
    return (
      <li
        className={`list-item list-item-list ${
          isReordering ? "list-item-reordering" : ""
        }`}
        onClick={onClick}
      >
        <div className="list-item-main">
          <div className="list-item-title">
            <strong>{title}</strong>
          </div>
        </div>

        {renderOrderMeta()}

        {renderActions()}
      </li>
    );
  }

  return (
    <li className="list-item list-item-grid" onClick={onClick}>
      <div className="list-item-content">
        <div className="list-item-title">
          <strong>{title}</strong>
        </div>

        {subtitle && <div className="list-item-subtitle">{subtitle}</div>}

        <div className="list-item-description-wrapper">
          <div
            className={`list-item-description ${
              tooltipVisible ? "show-tooltip" : ""
            }`}
            data-title={desc}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          >
            {desc}
          </div>
        </div>

        {renderOrderMeta()}
      </div>

      {renderActions()}
    </li>
  );
}

export default ListItem;
