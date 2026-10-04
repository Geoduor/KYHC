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
    <div className="overflow-x-auto">
      <table className="w-full min-w-full divide-y divide-slate-100 text-sm">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
            {columns.map((column) => (
              <th
                key={column.header}
                className={`px-3 py-2.5 font-semibold ${column.className ?? ""}`}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {rows.map((row) => (
            <tr key={row.id} className="hover:bg-slate-50/60">
              {columns.map((column) => (
                <td
                  key={column.header}
                  className={`px-3 py-2.5 ${column.className ?? ""}`}
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
    <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
      <span>
        Showing {Math.min(skip + 1, total)}–{Math.min(skip + limit, total)} of{" "}
        {total}
      </span>
      <div className="flex items-center gap-2">
        <Button
          variant="secondary"
          disabled={skip === 0}
          onClick={() => onChange(Math.max(0, skip - limit))}
        >
          Previous
        </Button>
        <span className="px-1 text-xs text-slate-500">
          Page {page} of {pageCount}
        </span>
        <Button
          variant="secondary"
          disabled={skip + limit >= total}
          onClick={() => onChange(skip + limit)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
