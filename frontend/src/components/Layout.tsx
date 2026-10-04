import { useEffect, useState, type ReactNode } from "react";
import { NavLink, useLocation } from "react-router-dom";

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
      className="h-5 w-5 shrink-0"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
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

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <img
        src="/logo.jpeg"
        alt="Kisumu Youngsters Hockey Club logo"
        className="h-10 w-10 shrink-0 rounded-xl bg-white object-contain shadow-card ring-1 ring-slate-200"
      />
      <div className="min-w-0">
        <p className="truncate text-sm font-bold text-slate-900">KYHC</p>
        <p className="truncate text-xs text-slate-500">
          Kisumu Youngsters HC
        </p>
      </div>
    </div>
  );
}

function NavList({
  isAdmin,
  onNavigate,
}: {
  isAdmin: boolean;
  onNavigate?: () => void;
}) {
  return (
    <nav aria-label="Primary" className="flex-1 space-y-1 overflow-y-auto px-3 py-3">
      {NAV_ITEMS.filter(
        (item) => !item.adminOnly || isAdmin,
      ).map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
              isActive
                ? "bg-brand-600 text-white shadow-card"
                : "text-slate-600 hover:bg-brand-50 hover:text-brand-800"
            }`
          }
        >
          {item.icon}
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

function UserFooter() {
  const { user, logout } = useAuth();

  return (
    <div className="border-t border-slate-100 p-4">
      <div className="flex items-center gap-3">
        <span
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-100 to-brand-200 text-xs font-bold text-brand-800"
          aria-hidden="true"
        >
          {user ? initials(user.full_name) : "?"}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-slate-800">
            {user?.full_name}
          </p>
          <p className="truncate text-xs text-slate-500">
            {user ? roleLabel(user.role) : ""}
          </p>
        </div>
      </div>
      <button
        onClick={logout}
        className="mt-3 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 active:scale-[0.99]"
      >
        Sign out
      </button>
    </div>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  const { user, isAdmin } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setDrawerOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  return (
    <div className="flex min-h-full bg-slate-100">
      {/* Mobile top bar */}
      <header className="fixed inset-x-0 top-0 z-40 flex h-16 items-center gap-3 border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur lg:hidden">
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          aria-label="Open navigation menu"
          aria-expanded={drawerOpen}
          className="flex h-10 w-10 items-center justify-center rounded-xl text-slate-700 transition hover:bg-slate-100 active:scale-95"
        >
          <svg
            className="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>
        <div className="min-w-0 flex-1">
          <Brand />
        </div>
        <span
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-800"
          aria-hidden="true"
        >
          {user ? initials(user.full_name) : "?"}
        </span>
      </header>

      {/* Drawer overlay (mobile only) */}
      {drawerOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/50 animate-fade-in lg:hidden"
          onClick={() => setDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar / drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col border-r border-slate-200 bg-white shadow-pop transition-transform duration-300 ease-out sm:w-64 lg:w-60 lg:translate-x-0 lg:shadow-none ${
          drawerOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Site navigation"
      >
        <div className="flex items-center justify-between px-5 pb-2 pt-5">
          <Brand />
          <button
            type="button"
            onClick={() => setDrawerOpen(false)}
            aria-label="Close navigation menu"
            className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 transition hover:bg-slate-100 lg:hidden"
          >
            <svg
              className="h-5 w-5"
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
        </div>

        <NavList
          isAdmin={isAdmin}
          onNavigate={() => setDrawerOpen(false)}
        />
        <UserFooter />
      </aside>

      {/* Content */}
      <main className="min-w-0 flex-1 px-4 pb-16 pt-20 sm:px-6 lg:ml-60 lg:px-8 lg:py-8 lg:pt-8">
        <div className="mx-auto w-full max-w-6xl animate-fade-up">
          {children}
        </div>
      </main>
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
    <div className="mb-5 flex flex-col gap-3 sm:mb-6 sm:flex-row sm:items-end sm:justify-between sm:gap-4">
      <div className="min-w-0">
        <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
        )}
      </div>
      {action && <div className="shrink-0 [&>button]:w-full sm:[&>button]:w-auto">{action}</div>}
    </div>
  );
}
