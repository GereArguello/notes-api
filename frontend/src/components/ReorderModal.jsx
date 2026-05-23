import { useEffect, useRef, useState } from "react";
import "./ReorderModal.css";

function ReorderModal({
  isOpen,
  itemId,
  itemLabel,
  currentPosition,
  maxPosition,
  onClose,
  onConfirm,
}) {
  const [value, setValue] = useState(() => String(currentPosition || 1));
  const inputRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return undefined;

    const focusTimeout = window.setTimeout(() => {
      inputRef.current?.focus();
      inputRef.current?.select();
    }, 10);

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.clearTimeout(focusTimeout);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [currentPosition, isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (event) => {
    event.preventDefault();
    onConfirm(Number(value));
  };

  return (
    <div
      className="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        aria-labelledby={`reorder-modal-title-${itemId}`}
        aria-modal="true"
        className="modal-card reorder-modal"
        role="dialog"
      >
        <div className="reorder-modal-eyebrow">Reordenar elemento</div>
        <h2 id={`reorder-modal-title-${itemId}`} className="reorder-modal-title">
          {itemLabel}
        </h2>
        <p className="reorder-modal-copy">
          Elegi la posicion final dentro de la lista.
        </p>

        <form onSubmit={handleSubmit}>
          <label className="reorder-modal-field">
            <span>Nueva posicion</span>
            <input
              ref={inputRef}
              max={maxPosition}
              min={1}
              step={1}
              type="number"
              value={value}
              onChange={(event) => setValue(event.target.value)}
            />
          </label>

          <p className="reorder-modal-hint">
            Posicion actual {currentPosition} de {maxPosition}
          </p>

          <div className="reorder-modal-actions">
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit">Mover</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ReorderModal;
