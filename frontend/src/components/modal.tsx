import { useEffect, type ReactNode } from "react";

function useLockBody(open: boolean) {
  useEffect(() => {
    if (!open) {
      return;
    }

    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        document.getElementById("modal-close-btn")?.click();
      }
    };

    document.addEventListener("keydown", onKey);

    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener("keydown", onKey);
    };
  }, [open ]);
}

export function Modal({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  useLockBody(open);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/50 p-0 animate-fade-in sm:items-center sm:p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
        className="flex max-h-[92dvh] w-full flex-col overflow-hidden rounded-t-3xl bg-white shadow-pop animate-fade-up sm:max-w-lg sm:rounded-2xl"
      >
        <header className="flex shrink-0 items-center justify-between border-b border-slate-100 px-4 py-4 sm:px-5">
          <h2 className="truncate text-sm font-bold text-slate-900">
            {title}
          </h2>
          <button
            id="modal-close-btn"
            onClick={onClose}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close dialog"
          >
            <svg
              className="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              aria-hidden="true"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </header>
        <div className="overflow-y-auto p-4 sm:p-5">{children}</div>
      </div>
    </div>
  );
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Delete",
  onConfirm,
  onCancel,
  busy = false,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  busy?: boolean;
}) {
  useLockBody(open);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/50 p-0 animate-fade-in sm:items-center sm:p-4">
      <div
        role="alertdialog"
        aria-modal="true"
        aria-label={title}
        aria-describedby="confirm-dialog-message"
        className="w-full max-w-sm rounded-t-3xl bg-white p-5 shadow-pop animate-fade-up sm:rounded-2xl"
      >
        <h2 className="text-sm font-bold text-slate-900">{title}</h2>
        <p
          id="confirm-dialog-message"
          className="mt-2 text-sm leading-relaxed text-slate-600"
        >
          {message}
        </p>
        <div className="mt-5 grid grid-cols-2 gap-2 sm:flex sm:justify-end">
          <button
            onClick={onCancel}
            className="min-h-11 rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 active:scale-[0.99]"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={busy}
            className="min-h-11 rounded-xl bg-gradient-to-b from-red-500 to-red-600 px-3.5 py-2.5 text-sm font-semibold text-white transition hover:from-red-600 hover:to-red-700 disabled:opacity-50 active:scale-[0.99]"
          >
            {busy ? "Deleting…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
