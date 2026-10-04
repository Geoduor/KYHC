import type {
  ButtonHTMLAttributes,
  InputHTMLAttributes,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

const buttonStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-gradient-to-b from-brand-600 to-brand-700 text-white shadow-card hover:from-brand-700 hover:to-brand-800 focus-visible:outline-brand-600 active:scale-[0.99]",
  secondary:
    "bg-white text-slate-700 border border-slate-300 shadow-sm hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-slate-400 active:scale-[0.99]",
  danger:
    "bg-gradient-to-b from-red-500 to-red-600 text-white shadow-card hover:from-red-600 hover:to-red-700 focus-visible:outline-red-600 active:scale-[0.99]",
  ghost:
    "bg-transparent text-slate-600 hover:bg-slate-100 focus-visible:outline-slate-400 active:scale-[0.99]",
};

const buttonSizes: Record<ButtonSize, string> = {
  sm: "min-h-9 px-3 py-1.5 text-xs",
  md: "min-h-10 px-3.5 py-2 text-sm",
  lg: "min-h-11 px-5 py-2.5 text-sm",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${buttonStyles[variant]} ${buttonSizes[size]} ${className}`}
      {...props}
    />
  );
}

const fieldControl =
  "min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-sm transition placeholder:text-slate-400 hover:border-slate-400 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15";

export function Input({
  label,
  error,
  hint,
  className = "",
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
  hint?: string;
}) {
  return (
    <label className="flex min-w-0 flex-col gap-1.5 text-sm" htmlFor={id}>
      {label && (
        <span className="font-semibold text-slate-700">{label}</span>
      )}
      <input id={id} className={`${fieldControl} ${className}`} {...props} />
      {error ? (
        <span role="alert" className="text-xs font-medium text-red-600">
          {error}
        </span>
      ) : hint ? (
        <span className="text-xs text-slate-400">{hint}</span>
      ) : null}
    </label>
  );
}

export function Select({
  label,
  children,
  className = "",
  id,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  children: ReactNode;
}) {
  return (
    <label className="flex min-w-0 flex-col gap-1.5 text-sm" htmlFor={id}>
      {label && (
        <span className="font-semibold text-slate-700">{label}</span>
      )}
      <select id={id} className={`${fieldControl} ${className}`} {...props}>
        {children}
      </select>
    </label>
  );
}

export function Textarea({
  label,
  className = "",
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
}) {
  return (
    <label className="flex min-w-0 flex-col gap-1.5 text-sm">
      {label && (
        <span className="font-semibold text-slate-700">{label}</span>
      )}
      <textarea
        className={`min-h-24 rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-sm transition placeholder:text-slate-400 hover:border-slate-400 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15 ${className}`}
        {...props}
      />
    </label>
  );
}

export function Card({
  title,
  subtitle,
  action,
  children,
  className = "",
}: {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-2xl border border-slate-200/80 bg-white shadow-card ${className}`}
    >
      {(title || action) && (
        <header className="flex flex-col gap-2 border-b border-slate-100 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
          <div className="min-w-0">
            {title && (
              <h2 className="truncate text-sm font-bold text-slate-900">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>
            )}
          </div>
          {action}
        </header>
      )}
      <div className="p-4 sm:p-5">{children}</div>
    </section>
  );
}

export function Badge({
  children,
  tone = "slate",
}: {
  children: ReactNode;
  tone?: "slate" | "green" | "red" | "amber" | "blue";
}) {
  const tones = {
    slate: "bg-slate-100 text-slate-700 ring-slate-200",
    green: "bg-brand-50 text-brand-800 ring-brand-200",
    red: "bg-red-50 text-red-700 ring-red-200",
    amber: "bg-amber-50 text-amber-800 ring-amber-200",
    blue: "bg-blue-50 text-blue-700 ring-blue-200",
  };

  return (
    <span
      className={`inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="flex items-center gap-3 py-8 text-sm text-slate-500"
      role="status"
      aria-live="polite"
    >
      <span
        className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600"
        aria-hidden="true"
      />
      {label}
    </div>
  );
}

export function ErrorNotice({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 sm:flex-row sm:items-center sm:justify-between"
    >
      <span>{message}</span>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center gap-2 py-10 text-center">
      <span
        className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-100 text-lg"
        aria-hidden="true"
      >
        ◌
      </span>
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  );
}
