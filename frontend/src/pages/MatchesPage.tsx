import { useEffect, useMemo, useState, type FormEvent } from "react";

import { DataTable, Pagination } from "../components/DataTable";
import { PageHeader } from "../components/Layout";
import { ConfirmDialog, Modal } from "../components/modal";
import {
  Badge,
  Button,
  Card,
  Input,
  Select,
} from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useList } from "../hooks/useList";
import { ApiError, api } from "../lib/api";
import { formatDateTime } from "../lib/format";
import type { Match, Team } from "../types";

interface MatchForm {
  home_team_id: string;
  away_team_id: string;
  competition: string;
  venue: string;
  match_date: string;
  status: string;
  home_score: string;
  away_score: string;
  notes: string;
}

const EMPTY_FORM: MatchForm = {
  home_team_id: "",
  away_team_id: "",
  competition: "",
  venue: "",
  match_date: "",
  status: "Scheduled",
  home_score: "0",
  away_score: "0",
  notes: "",
};

const STATUS_TONES: Record<string, "green" | "amber" | "red" | "slate"> =
  {
    Completed: "green",
    Scheduled: "amber",
    Postponed: "slate",
    Cancelled: "red",
  };

export default function MatchesPage() {
  const { canManage } = useAuth();

  const [statusFilter, setStatusFilter] = useState("");
  const [teamFilter, setTeamFilter] = useState("");

  const list = useList<Match>("/matches/", {
    status: statusFilter,
    team_id: teamFilter,
  });

  const [teams, setTeams] = useState<Team[]>([]);

  useEffect(() => {
    api
      .get<{ items: Team[] }>("/teams/?limit=200")
      .then((page) => setTeams(page.items))
      .catch(() => setTeams([]));
  }, []);

  const teamNames = useMemo(
    () => new Map(teams.map((team) => [team.id, team.name])),
    [teams],
  );

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Match | null>(null);
  const [form, setForm] = useState<MatchForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleting, setDeleting] = useState<Match | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  function openCreate() {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setFormOpen(true);
  }

  function openEdit(match: Match) {
    setEditing(match);
    setForm({
      home_team_id: String(match.home_team_id),
      away_team_id: String(match.away_team_id),
      competition: match.competition,
      venue: match.venue,
      match_date: match.match_date.slice(0, 16),
      status: match.status,
      home_score: String(match.home_score),
      away_score: String(match.away_score),
      notes: match.notes ?? "",
    });
    setFormError(null);
    setFormOpen(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    const payload = {
      home_team_id: Number(form.home_team_id),
      away_team_id: Number(form.away_team_id),
      competition: form.competition,
      venue: form.venue,
      match_date: form.match_date,
      status: form.status,
      home_score: Number(form.home_score) || 0,
      away_score: Number(form.away_score) || 0,
      notes: form.notes || null,
    };

    try {
      if (editing) {
        await api.put(`/matches/${editing.id}`, payload);
      } else {
        await api.post("/matches/", payload);
      }

      setFormOpen(false);
      await list.reload();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not save match",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!deleting) {
      return;
    }

    setDeleteBusy(true);

    try {
      await api.delete(`/matches/${deleting.id}`);
      setDeleting(null);
      await list.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not delete match",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Matches"
        subtitle="Fixtures, results and match events."
        action={
          canManage ? (
            <Button
              onClick={openCreate}
              disabled={teams.length < 2}
            >
              Add match
            </Button>
          ) : undefined
        }
      />

      <Card>
        <div className="mb-4 flex flex-wrap gap-3">
          <Select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="w-48"
          >
            <option value="">All statuses</option>
            <option>Scheduled</option>
            <option>Completed</option>
            <option>Postponed</option>
            <option>Cancelled</option>
          </Select>

          <Select
            value={teamFilter}
            onChange={(event) => setTeamFilter(event.target.value)}
            className="w-56"
          >
            <option value="">All teams</option>
            {teams.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </Select>
        </div>

        <DataTable
          columns={[
            {
              header: "Fixture",
              render: (match) => (
                <div>
                  <p className="font-medium text-slate-800">
                    {teamNames.get(match.home_team_id) ??
                      `#${match.home_team_id}`}{" "}
                    <span className="text-slate-400">vs</span>{" "}
                    {teamNames.get(match.away_team_id) ??
                      `#${match.away_team_id}`}
                  </p>
                  <p className="text-xs text-slate-500">
                    {match.competition}
                  </p>
                </div>
              ),
            },
            {
              header: "Score",
              render: (match) =>
                match.status === "Completed" ? (
                  <span className="font-semibold text-slate-800">
                    {match.home_score}–{match.away_score}
                  </span>
                ) : (
                  <span className="text-slate-400">—</span>
                ),
            },
            {
              header: "Date",
              render: (match) => formatDateTime(match.match_date),
            },
            {
              header: "Venue",
              render: (match) => match.venue,
            },
            {
              header: "Status",
              render: (match) => (
                <Badge tone={STATUS_TONES[match.status] ?? "slate"}>
                  {match.status}
                </Badge>
              ),
            },
            ...(canManage
              ? [
                  {
                    header: "",
                    className: "text-right",
                    render: (match: Match) => (
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => openEdit(match)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          onClick={() => setDeleting(match)}
                        >
                          Delete
                        </Button>
                      </div>
                    ),
                  },
                ]
              : []),
          ]}
          rows={list.rows}
          loading={list.loading}
          error={list.error}
          onRetry={list.reload}
          emptyMessage="No matches scheduled yet."
        />

        <Pagination
          total={list.total}
          skip={list.skip}
          limit={list.limit}
          onChange={list.setSkip}
        />
      </Card>

      <Modal
        open={formOpen}
        title={editing ? "Edit match" : "Add match"}
        onClose={() => setFormOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Home team"
              required
              value={form.home_team_id}
              onChange={(event) =>
                setForm({
                  ...form,
                  home_team_id: event.target.value,
                })
              }
            >
              <option value="" disabled>
                Select
              </option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </Select>
            <Select
              label="Away team"
              required
              value={form.away_team_id}
              onChange={(event) =>
                setForm({
                  ...form,
                  away_team_id: event.target.value,
                })
              }
            >
              <option value="" disabled>
                Select
              </option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Competition"
              required
              value={form.competition}
              onChange={(event) =>
                setForm({
                  ...form,
                  competition: event.target.value,
                })
              }
            />
            <Input
              label="Venue"
              required
              value={form.venue}
              onChange={(event) =>
                setForm({ ...form, venue: event.target.value })
              }
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Date & time"
              type="datetime-local"
              required
              value={form.match_date}
              onChange={(event) =>
                setForm({
                  ...form,
                  match_date: event.target.value,
                })
              }
            />
            <Select
              label="Status"
              value={form.status}
              onChange={(event) =>
                setForm({ ...form, status: event.target.value })
              }
            >
              <option>Scheduled</option>
              <option>Completed</option>
              <option>Postponed</option>
              <option>Cancelled</option>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Home score"
              type="number"
              min={0}
              value={form.home_score}
              onChange={(event) =>
                setForm({
                  ...form,
                  home_score: event.target.value,
                })
              }
            />
            <Input
              label="Away score"
              type="number"
              min={0}
              value={form.away_score}
              onChange={(event) =>
                setForm({
                  ...form,
                  away_score: event.target.value,
                })
              }
            />
          </div>

          <Input
            label="Notes"
            value={form.notes}
            onChange={(event) =>
              setForm({ ...form, notes: event.target.value })
            }
          />

          {formError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError}
            </p>
          )}

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setFormOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save match"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        title="Delete match"
        message="Delete this match and all of its recorded events?"
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
