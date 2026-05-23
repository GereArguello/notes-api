import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export function usePaginatedResource({
  fetchDataFn,
  deleteFn,
  pageSize = 20,
}) {
  const [items, setItems] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    size: pageSize,
    total: 0,
  });
  const [loading, setLoading] = useState(true);

  const [searchParams, setSearchParams] = useSearchParams();

  const currentPage = Math.max(1, Number(searchParams.get("page")) || 1);
  const totalPages = Math.max(1, Math.ceil(pagination.total / pagination.size));
  const hasPreviousPage = currentPage > 1;
  const hasNextPage = currentPage < totalPages;

  const goToPage = useCallback(
    (page) => {
      const nextPage = Math.max(1, page);
      const nextParams = new URLSearchParams(searchParams);

      if (nextPage === 1) {
        nextParams.delete("page");
      } else {
        nextParams.set("page", String(nextPage));
      }

      setSearchParams(nextParams);
    },
    [searchParams, setSearchParams]
  );

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchDataFn(currentPage);

      const size = data.size || pageSize;
      const total = data.total || 0;
      const fetchedTotalPages = Math.max(1, Math.ceil(total / size));

      setItems(data.items || []);
      setPagination({
        page: data.page || currentPage,
        size,
        total,
      });

      if (currentPage > fetchedTotalPages) {
        goToPage(fetchedTotalPages);
      }
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentPage, fetchDataFn, goToPage, pageSize]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleDelete = useCallback(
    async (id) => {
      await deleteFn(id);

      const remainingItems = items.length - 1;
      const previousTotalPages = Math.max(
        1,
        Math.ceil((pagination.total - 1) / pagination.size)
      );

      if (
        remainingItems === 0 &&
        currentPage > 1 &&
        currentPage > previousTotalPages
      ) {
        goToPage(currentPage - 1);
        return;
      }

      await fetchItems();
    },
    [
      currentPage,
      deleteFn,
      fetchItems,
      goToPage,
      items.length,
      pagination.size,
      pagination.total,
    ]
  );

  return {
    items,
    loading,
    currentPage,
    hasPreviousPage,
    hasNextPage,
    totalItems: pagination.total,
    goToPage,
    handleDelete,
    updateItems: setItems,
    refetch: fetchItems,
  };
}
