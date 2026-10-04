import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Button, Input } from "../components/ui";
import { InstallButton } from "../components/InstallButton";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../lib/api";

const HIGHLIGHTS = [
  { title: "Teams & squads", detail: "Youth, senior and veteran sides in one register." },
  { title: "Fixtures & events", detail: "Schedule matches and capture goals, cards and subs." },
  { title: "Training", detail: "Plan sessions and track attendance by player." },
  { title: "Statistics", detail: "Per-match numbers with team and player aggregates." },
];

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    setBusy(true);
    setError(null);

    try {
      await login(email.trim(), password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to sign in. Check your connection.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-dvh flex-col bg-slate-100 lg:flex-row">
      {/* Brand panel */}
      <section
        aria-label="About KYHC Club Management"
        className="relative overflow-hidden bg-gradient-to-br from-brand-900 via-brand-800 to-brand-950 px-6 py-10 text-white sm:px-10 lg:flex lg:w-[46%] lg:flex-col lg:justify-between lg:px-12 lg:py-12"
      >
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-accent-400/15 blur-2xl"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -bottom-28 -left-20 h-72 w-72 rounded-full bg-brand-400/20 blur-2xl"
          aria-hidden="true"
        />

        <div className="relative flex items-center gap-3">
          <img
            src="/logo.png"
            alt="Kisumu Youngstars Hockey Club logo"
            className="h-12 w-12 rounded-2xl bg-white object-contain shadow-card ring-1 ring-white/20"
          />
          <div>
            <p className="text-sm font-bold tracking-tight">KYHC</p>
            <p className="text-xs text-brand-200">
              Kisumu Youngstars Hockey Club
            </p>
          </div>
        </div>

        <div className="relative mt-8 lg:mt-0">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-accent-400">
            Club management
          </p>
          <h1 className="mt-3 max-w-md text-3xl font-extrabold leading-tight tracking-tight sm:text-4xl">
            The whole club, in one place.
          </h1>
          <p className="mt-3 max-w-md text-sm leading-relaxed text-brand-100 sm:text-base">
            Squads, fixtures, training sessions and statistics for
            Kisumu Youngstars Hockey Club — built for coaches,
            managers and admins.
          </p>

          <ul className="mt-8 hidden gap-3 lg:grid">
            {HIGHLIGHTS.map((item) => (
              <li
                key={item.title}
                className="flex items-start gap-3 rounded-2xl bg-white/10 p-4 ring-1 ring-white/10 backdrop-blur"
              >
                <span
                  className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-400 text-[11px] font-extrabold text-brand-950"
                  aria-hidden="true"
                >
                  ✓
                </span>
                <span>
                  <span className="block text-sm font-bold">
                    {item.title}
                  </span>
                  <span className="block text-xs leading-relaxed text-brand-100">
                    {item.detail}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </div>

        <p className="relative mt-8 hidden text-xs text-brand-200/80 lg:block">
          Kisumu, Kenya — youth hockey since day one.
        </p>
      </section>

      {/* Sign-in panel */}
      <section
        aria-label="Sign in"
        className="flex flex-1 items-center justify-center px-4 py-10 sm:px-8"
      >
        <div className="w-full max-w-sm animate-fade-up">
          <div className="mb-5 text-center lg:text-left">
            <h2 className="text-xl font-extrabold tracking-tight text-slate-900 sm:text-2xl">
              Welcome back
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Sign in to manage your club.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-4 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card sm:p-6"
          >
            <Input
              id="login-email"
              label="Email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@kyhc.local"
            />

            <Input
              id="login-password"
              label="Password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />

            {error && (
              <p
                role="alert"
                className="rounded-xl bg-red-50 px-3.5 py-2.5 text-sm font-medium text-red-700 ring-1 ring-inset ring-red-200"
              >
                {error}
              </p>
            )}

            <Button
              type="submit"
              size="lg"
              className="w-full"
              disabled={busy}
            >
              {busy ? "Signing in…" : "Sign in"}
            </Button>

            <p className="text-center text-xs leading-relaxed text-slate-400">
              Use the super admin account created during setup.
            </p>
            <InstallButton className="w-full" />
          </form>
        </div>
      </section>
    </main>
  );
}
