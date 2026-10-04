import { useCallback, useEffect, useState } from "react";

import { ApiError, api, buildQuery } from "../lib/api";
import type { Page } from "../types";

export function useList<T>(
  basePath: string,
  filters: Record<string, string | number | boolean | undefined>,
) {
  const [data, setData] = useState<Page<T> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const limit = 25;

  const filterKey = JSON.stringify(filters);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const query = buildQuery({
        ...JSON.parse(filterKey),
        skip,
        limit,
      });

      const page = await api.get<Page<T>>(`${basePath}${query}`);

      setData(page);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load data",
      );
    } finally {
      setLoading(false);
    }
  }, [basePath, filterKey, skip]);

  useEffect(() => {
    void reload();
  }, [reload]);

  // Reset to the first page when filters change.
  useEffect(() => {
    setSkip(0);
  }, [filterKey]);

  return {
    data,
    rows: data?.items ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    skip,
    limit,
    setSkip,
    reload,
  };
}
