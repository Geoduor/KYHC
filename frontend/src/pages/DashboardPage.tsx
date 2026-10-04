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
}

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

        setStats([
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
        ]);

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
        <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats === null && !error
          ? Array.from({ length: 4 }).map((_, index) => (
              <Card key={index}>
                <Spinner label="" />
              </Card>
            ))
          : stats?.map((stat) => (
              <Card key={stat.label}>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {stat.label}
                </p>
                <p className="mt-2 text-3xl font-semibold text-slate-900">
                  {stat.value}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  {stat.hint}
                </p>
              </Card>
            ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Upcoming matches">
          {upcoming === null ? (
            <Spinner label="" />
          ) : upcoming.length === 0 ? (
            <p className="py-6 text-center text-sm text-slate-500">
              No scheduled matches.
            </p>
          ) : (
            <ul className="divide-y divide-slate-50">
              {upcoming.map((match) => (
                <li
                  key={match.id}
                  className="flex items-center justify-between py-3"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-800">
                      {match.competition}
                    </p>
                    <p className="text-xs text-slate-500">
                      {match.venue}
                    </p>
                  </div>
                  <span className="text-xs text-slate-500">
                    {formatDateTime(match.match_date)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Getting started">
          <ul className="space-y-3 text-sm text-slate-600">
            <li className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                1
              </span>
              Create teams under <strong>Teams</strong>, then add
              players and coaches to them.
            </li>
            <li className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                2
              </span>
              Schedule fixtures and record match events under{" "}
              <strong>Matches</strong>.
            </li>
            <li className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                3
              </span>
              Plan sessions and track attendance under{" "}
              <strong>Training</strong>.
            </li>
            <li className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                4
              </span>
              Record per-match numbers and review aggregates under{" "}
              <strong>Statistics</strong>.
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
