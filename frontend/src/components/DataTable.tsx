import type { ReactNode } from "react";

import { Button, EmptyState, ErrorNotice, Spinner } from "./ui";

export interface Column<T> {
  header: string;
  render: (row: T) => ReactNode;
  className?: string;
}

export function DataTable<T extends { id: number }>({
  columns,
  rows,
  loading,
  error,
  onRetry,
  emptyMessage = "Nothing to show yet.",
}: {
  columns: Column<T>[];
  rows: T[];
  loading: boolean;
  error: string | null;
  onRetry?: () => void;
  emptyMessage?: string;
}) {
  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorNotice message={error} onRetry={onRetry} />;
  }

  if (rows.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
      <table className="w-full min-w-[640px] divide-y divide-slate-100 text-sm">
        <thead className="sticky top-0">
          <tr className="bg-white text-left text-[11px] uppercase tracking-wider text-slate-500">
            {columns.map((column) => (
              <th
                key={column.header}
                scope="col"
                className={`whitespace-nowrap px-3 py-3 font-bold ${column.className ?? ""}`}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
            <tr
              key={row.id}
              className="transition hover:bg-brand-50/50"
            >
              {columns.map((column) => (
                <td
                  key={column.header}
                  className={`px-3 py-3 align-middle ${column.className ?? ""}`}
                >
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Pagination({
  total,
  skip,
  limit,
  onChange,
}: {
  total: number;
  skip: number;
  limit: number;
  onChange: (skip: number) => void;
}) {
  const page = Math.floor(skip / limit) + 1;
  const pageCount = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="mt-4 flex flex-col gap-3 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">
      <span className="text-xs sm:text-sm">
        Showing {total === 0 ? 0 : Math.min(skip + 1, total)}–
        {Math.min(skip + limit, total)} of {total}
      </span>
      <div className="flex items-center justify-between gap-2 sm:justify-end">
        <Button
          variant="secondary"
          size="sm"
          disabled={skip === 0}
          onClick={() => onChange(Math.max(0, skip - limit))}
        >
          ← Prev
        </Button>
        <span className="px-1 text-xs font-medium text-slate-500">
          Page {page} of {pageCount}
        </span>
        <Button
          variant="secondary"
          size="sm"
          disabled={skip + limit >= total}
          onClick={() => onChange(skip + limit)}
        >
          Next →
        </Button>
      </div>
    </div>
  );
}
