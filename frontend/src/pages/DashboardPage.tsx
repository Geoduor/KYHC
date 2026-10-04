import { useEffect, useState } from "react";

import { PageHeader } from "../components/Layout";
import { Card, Spinner } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { formatDateTime } from "../lib/format";
import type {
  Coach,
  Match,
  Page,
  Player,
  Team,
} from "../types";

interface Stat {
  label: string;
  value: number | null;
  hint: string;
  icon: string;
  gradient: string;
}

const STAT_STYLES: Array<Pick<Stat, "icon" | "gradient">> = [
  { icon: "◈", gradient: "from-brand-500 to-brand-700" },
  { icon: "●", gradient: "from-accent-400 to-brand-600" },
  { icon: "★", gradient: "from-brand-700 to-brand-950" },
  { icon: "◎", gradient: "from-brand-400 to-brand-800" },
];

export default function DashboardPage() {
  const { user } = useAuth();

  const [stats, setStats] = useState<Stat[] | null>(null);
  const [upcoming, setUpcoming] = useState<Match[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [teams, players, coaches, matches] = await Promise.all([
          api.get<Page<Team>>("/teams/?limit=1"),
          api.get<Page<Player>>("/players/?limit=1"),
          api.get<Page<Coach>>("/coaches/?limit=1"),
          api.get<Page<Match>>(
            "/matches/?limit=5&upcoming_only=true",
          ),
        ]);

        if (cancelled) {
          return;
        }

        const defs = [
          {
            label: "Teams",
            value: teams.total,
            hint: "Active and archived",
          },
          {
            label: "Players",
            value: players.total,
            hint: "Registered in the club",
          },
          {
            label: "Coaches",
            value: coaches.total,
            hint: "Coaching staff",
          },
          {
            label: "Matches",
            value: matches.total,
            hint: "Scheduled",
          },
        ];

        setStats(
          defs.map((def, index) => ({
            ...def,
            ...STAT_STYLES[index % STAT_STYLES.length],
          })),
        );

        setUpcoming(matches.items);
      } catch {
        if (!cancelled) {
          setError("Could not load dashboard data.");
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <PageHeader
        title={`Welcome back${user ? `, ${user.full_name.split(" ")[0]}` : ""}`}
        subtitle="A snapshot of the club's activity."
      />

      {error && (
        <p
          role="alert"
          className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-sm font-medium text-red-700 ring-1 ring-inset ring-red-200"
        >
          {error}
        </p>
      )}

      <div className="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4">
        {stats === null && !error
          ? Array.from({ length: 4 }).map((_, index) => (
              <Card key={index}>
                <Spinner label="" />
              </Card>
            ))
          : stats?.map((stat) => (
              <Card key={stat.label} className="overflow-hidden">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 sm:text-xs">
                      {stat.label}
                    </p>
                    <p className="mt-1 text-2xl font-extrabold tabular-nums tracking-tight text-slate-900 sm:text-3xl">
                      {stat.value}
                    </p>
                    <p className="mt-1 truncate text-[11px] text-slate-400 sm:text-xs">
                      {stat.hint}
                    </p>
                  </div>
                  <span
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br text-base text-white shadow-card sm:h-11 sm:w-11 ${stat.gradient}`}
                    aria-hidden="true"
                  >
                    {stat.icon}
                  </span>
                </div>
              </Card>
            ))}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 sm:mt-6 lg:grid-cols-2">
        <Card
          title="Upcoming matches"
          subtitle="Next scheduled fixtures"
        >
          {upcoming === null ? (
            <Spinner label="" />
          ) : upcoming.length === 0 ? (
            <p className="py-6 text-center text-sm text-slate-500">
              No scheduled matches.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {upcoming.map((match) => (
                <li
                  key={match.id}
                  className="flex items-center justify-between gap-3 py-3"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-800">
                      {match.competition}
                    </p>
                    <p className="truncate text-xs text-slate-500">
                      {match.venue}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600">
                    {formatDateTime(match.match_date)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Getting started" subtitle="Four steps to matchday">
          <ol className="space-y-3 text-sm text-slate-600">
            {[
              ["Teams", "Create teams, then add players and coaches to them."],
              ["Matches", "Schedule fixtures and record match events."],
              ["Training", "Plan sessions and track attendance."],
              ["Statistics", "Record numbers and review aggregates."],
            ].map(([title, detail], index) => (
              <li key={title} className="flex gap-3">
                <span
                  className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white"
                  aria-hidden="true"
                >
                  {index + 1}
                </span>
                <p className="min-w-0 leading-relaxed">
                  <strong className="font-semibold text-slate-800">
                    {title}
                  </strong>{" "}
                  — {detail}
                </p>
              </li>
            ))}
          </ol>
        </Card>
      </div>
    </div>
  );
}
