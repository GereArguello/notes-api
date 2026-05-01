function PaginationFooter({
  currentPage,
  hasPreviousPage,
  hasNextPage,
  onPreviousPage,
  onNextPage,
  onBack,
  backLabel,
}) {
  return (
    <div className="pagination-footer">
      {hasPreviousPage ? (
        <button
          type="button"
          className="pagination-arrow"
          onClick={onPreviousPage}
          aria-label={`Ir a la pagina ${currentPage - 1}`}
        >
          {"<"}
        </button>
      ) : (
        <span className="pagination-arrow-placeholder" aria-hidden="true" />
      )}

      <div className="pagination-center">
        <button type="button" onClick={onBack}>
          {backLabel}
        </button>
        <span className="pagination-page-indicator">Pagina {currentPage}</span>
      </div>

      {hasNextPage ? (
        <button
          type="button"
          className="pagination-arrow"
          onClick={onNextPage}
          aria-label={`Ir a la pagina ${currentPage + 1}`}
        >
          {">"}
        </button>
      ) : (
        <span className="pagination-arrow-placeholder" aria-hidden="true" />
      )}
    </div>
  );
}

export default PaginationFooter;
