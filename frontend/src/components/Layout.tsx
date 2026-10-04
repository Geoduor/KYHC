import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { initials, roleLabel } from "../lib/format";

interface NavItem {
  to: string;
  label: string;
  icon: ReactNode;
  adminOnly?: boolean;
}

function Icon({ path }: { path: string }) {
  return (
    <svg
      className="h-4 w-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={path} />
    </svg>
  );
}

const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Dashboard", icon: <Icon path="M3 12l9-9 9 9M5 10v10h14V10" /> },
  { to: "/teams", label: "Teams", icon: <Icon path="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" /> },
  { to: "/players", label: "Players", icon: <Icon path="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z" /> },
  { to: "/coaches", label: "Coaches", icon: <Icon path="M12 2l3 7h7l-5.5 4 2 7L12 16l-6.5 4 2-7L2 9h7z" /> },
  { to: "/matches", label: "Matches", icon: <Icon path="M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20" /> },
  { to: "/training", label: "Training", icon: <Icon path="M6 5v14M18 5v14M6 12h12M4 8h4M4 16h4M16 8h4M16 16h4" /> },
  { to: "/statistics", label: "Statistics", icon: <Icon path="M3 3v18h18M8 17V9M13 17V5M18 17v-6" /> },
  { to: "/users", label: "Users", icon: <Icon path="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM22 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />, adminOnly: true },
];

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout, isAdmin } = useAuth();

  return (
    <div className="flex min-h-full">
      <aside className="fixed inset-y-0 flex w-60 flex-col border-r border-slate-200 bg-white">
        <div className="flex items-center gap-3 px-5 py-5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
            KY
          </span>
          <div>
            <p className="text-sm font-semibold text-slate-800">KYHC</p>
            <p className="text-xs text-slate-500">
              Kisumu Youngsters HC
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-2">
          {NAV_ITEMS.filter(
            (item) => !item.adminOnly || isAdmin,
          ).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-100 p-4">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-600">
              {user ? initials(user.full_name) : "?"}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-800">
                {user?.full_name}
              </p>
              <p className="truncate text-xs text-slate-500">
                {user ? roleLabel(user.role) : ""}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="mt-3 w-full rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition hover:bg-slate-50"
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="ml-60 flex-1 px-8 py-8">{children}</main>
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
        {subtitle && (
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
        )}
      </div>
      {action}
    </div>
  );
}
