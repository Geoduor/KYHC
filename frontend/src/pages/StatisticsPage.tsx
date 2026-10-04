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
import type {
  Match,
  Page,
  Player,
  PlayerStatistic,
  PlayerSummary,
  Team,
  TeamSummary,
} from "../types";

interface StatForm {
  player_id: string;
  match_id: string;
  goals: string;
  assists: string;
  shots: string;
  shots_on_target: string;
  passes: string;
  successful_passes: string;
  interceptions: string;
  tackles: string;
  green_cards: string;
  yellow_cards: string;
  red_cards: string;
  minutes_played: string;
  rating: string;
  mvp: boolean;
}

const EMPTY_STAT: StatForm = {
  player_id: "",
  match_id: "",
  goals: "0",
  assists: "0",
  shots: "0",
  shots_on_target: "0",
  passes: "0",
  successful_passes: "0",
  interceptions: "0",
  tackles: "0",
  green_cards: "0",
  yellow_cards: "0",
  red_cards: "0",
  minutes_played: "0",
  rating: "0",
  mvp: false,
};

function SummaryTile({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg bg-slate-50 px-4 py-3">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">
        {value}
      </p>
    </div>
  );
}

export default function StatisticsPage() {
  const { canCoach } = useAuth();

  const [teams, setTeams] = useState<Team[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);

  const [teamId, setTeamId] = useState("");
  const [playerId, setPlayerId] = useState("");

  const [teamSummary, setTeamSummary] =
    useState<TeamSummary | null>(null);
  const [playerSummary, setPlayerSummary] =
    useState<PlayerSummary | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(
    null,
  );

  const playerFilter = useMemo(() => playerId, [playerId]);

  const list = useList<PlayerStatistic>("/player-statistics/", {
    player_id: playerFilter,
  });

  useEffect(() => {
    api
      .get<Page<Team>>("/teams/?limit=200")
      .then((page) => setTeams(page.items))
      .catch(() => setTeams([]));

    api
      .get<Page<Player>>("/players/?limit=200")
      .then((page) => setPlayers(page.items))
      .catch(() => setPlayers([]));

    api
      .get<Page<Match>>("/matches/?limit=200")
      .then((page) => setMatches(page.items))
      .catch(() => setMatches([]));
  }, []);

  const playerNames = useMemo(
    () =>
      new Map(
        players.map((player) => [
          player.id,
          `${player.first_name} ${player.last_name}`,
        ]),
      ),
    [players],
  );

  const matchLabels = useMemo(
    () =>
      new Map(
        matches.map((match) => [
          match.id,
          `${match.competition} — ${new Date(
            match.match_date,
          ).toLocaleDateString()}`,
        ]),
      ),
    [matches],
  );

  useEffect(() => {
    if (!teamId) {
      setTeamSummary(null);
      return;
    }

    setSummaryError(null);

    api
      .get<TeamSummary>(`/statistics/team/${teamId}`)
      .then(setTeamSummary)
      .catch((err) =>
        setSummaryError(
          err instanceof ApiError
            ? err.message
            : "Could not load team summary",
        ),
      );
  }, [teamId]);

  useEffect(() => {
    if (!playerId) {
      setPlayerSummary(null);
      return;
    }

    setSummaryError(null);

    api
      .get<PlayerSummary>(`/statistics/player/${playerId}`)
      .then(setPlayerSummary)
      .catch((err) =>
        setSummaryError(
          err instanceof ApiError
            ? err.message
            : "Could not load player summary",
        ),
      );
  }, [playerId]);

  // Statistic form state.
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<PlayerStatistic | null>(
    null,
  );
  const [form, setForm] = useState<StatForm>(EMPTY_STAT);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleting, setDeleting] = useState<PlayerStatistic | null>(
    null,
  );
  const [deleteBusy, setDeleteBusy] = useState(false);

  function openCreate() {
    setEditing(null);
    setForm({
      ...EMPTY_STAT,
      player_id: players[0] ? String(players[0].id) : "",
      match_id: matches[0] ? String(matches[0].id) : "",
    });
    setFormError(null);
    setFormOpen(true);
  }

  function openEdit(statistic: PlayerStatistic) {
    setEditing(statistic);
    setForm({
      player_id: String(statistic.player_id),
      match_id: String(statistic.match_id),
      goals: String(statistic.goals),
      assists: String(statistic.assists),
      shots: String(statistic.shots),
      shots_on_target: String(statistic.shots_on_target),
      passes: String(statistic.passes),
      successful_passes: String(statistic.successful_passes),
      interceptions: String(statistic.interceptions),
      tackles: String(statistic.tackles),
      green_cards: String(statistic.green_cards),
      yellow_cards: String(statistic.yellow_cards),
      red_cards: String(statistic.red_cards),
      minutes_played: String(statistic.minutes_played),
      rating: String(statistic.rating),
      mvp: statistic.mvp,
    });
    setFormError(null);
    setFormOpen(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    const payload = {
      player_id: Number(form.player_id),
      match_id: Number(form.match_id),
      goals: Number(form.goals) || 0,
      assists: Number(form.assists) || 0,
      shots: Number(form.shots) || 0,
      shots_on_target: Number(form.shots_on_target) || 0,
      passes: Number(form.passes) || 0,
      successful_passes: Number(form.successful_passes) || 0,
      interceptions: Number(form.interceptions) || 0,
      tackles: Number(form.tackles) || 0,
      green_cards: Number(form.green_cards) || 0,
      yellow_cards: Number(form.yellow_cards) || 0,
      red_cards: Number(form.red_cards) || 0,
      minutes_played: Number(form.minutes_played) || 0,
      rating: Number(form.rating) || 0,
      mvp: form.mvp,
    };

    try {
      if (editing) {
        const { player_id, match_id, ...update } = payload;
        void player_id;
        void match_id;

        await api.put(
          `/player-statistics/${editing.id}`,
          update,
        );
      } else {
        await api.post("/player-statistics/", payload);
      }

      setFormOpen(false);
      await list.reload();
    } catch (err) {
      setFormError(
        err instanceof ApiError
          ? err.message
          : "Could not save statistics",
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
      await api.delete(`/player-statistics/${deleting.id}`);
      setDeleting(null);
      await list.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not delete statistics",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  const numberField = (
    key: keyof StatForm,
    label: string,
  ) => (
    <Input
      label={label}
      type="number"
      min={0}
      value={String(form[key])}
      onChange={(event) =>
        setForm({ ...form, [key]: event.target.value })
      }
    />
  );

  return (
    <div>
      <PageHeader
        title="Statistics"
        subtitle="Aggregates and per-match player numbers."
        action={
          canCoach ? (
            <Button
              onClick={openCreate}
              disabled={players.length === 0 || matches.length === 0}
            >
              Add record
            </Button>
          ) : undefined
        }
      />

      {summaryError && (
        <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {summaryError}
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Team summary">
          <Select
            value={teamId}
            onChange={(event) => setTeamId(event.target.value)}
          >
            <option value="">Select a team…</option>
            {teams.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </Select>

          {teamSummary && (
            <>
              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <SummaryTile
                  label="Played"
                  value={teamSummary.played}
                />
                <SummaryTile label="Wins" value={teamSummary.wins} />
                <SummaryTile
                  label="Draws"
                  value={teamSummary.draws}
                />
                <SummaryTile
                  label="Losses"
                  value={teamSummary.losses}
                />
              </div>
              <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
                <SummaryTile
                  label="Goals for"
                  value={teamSummary.goals_for}
                />
                <SummaryTile
                  label="Goals against"
                  value={teamSummary.goals_against}
                />
                <SummaryTile
                  label="Difference"
                  value={
                    teamSummary.goal_difference > 0
                      ? `+${teamSummary.goal_difference}`
                      : teamSummary.goal_difference
                  }
                />
              </div>
              <div className="mt-3 flex gap-3 text-xs text-slate-500">
                <span>
                  Goal events: {teamSummary.goal_events}
                </span>
                <span>
                  Yellow cards: {teamSummary.yellow_cards}
                </span>
                <span>Red cards: {teamSummary.red_cards}</span>
              </div>
            </>
          )}
        </Card>

        <Card title="Player summary">
          <Select
            value={playerId}
            onChange={(event) => setPlayerId(event.target.value)}
          >
            <option value="">Select a player…</option>
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.first_name} {player.last_name}
              </option>
            ))}
          </Select>

          {playerSummary && (
            <>
              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <SummaryTile
                  label="Goals"
                  value={playerSummary.goals}
                />
                <SummaryTile
                  label="Assists"
                  value={playerSummary.assists}
                />
                <SummaryTile
                  label="Yellow"
                  value={playerSummary.cards.yellow}
                />
                <SummaryTile
                  label="Red"
                  value={playerSummary.cards.red}
                />
              </div>
              <p className="mt-3 text-xs text-slate-500">
                Green cards: {playerSummary.cards.green}
              </p>
            </>
          )}
        </Card>
      </div>

      <div className="mt-6">
        <Card title="Per-match records">
          <div className="mb-4 flex flex-wrap gap-3">
            <Select
              value={playerId}
              onChange={(event) => setPlayerId(event.target.value)}
              className="w-full sm:w-64"
            >
              <option value="">All players</option>
              {players.map((player) => (
                <option key={player.id} value={player.id}>
                  {player.first_name} {player.last_name}
                </option>
              ))}
            </Select>
          </div>

          <DataTable
            columns={[
              {
                header: "Player",
                render: (row) =>
                  playerNames.get(row.player_id) ?? `#${row.player_id}`,
              },
              {
                header: "Match",
                render: (row) =>
                  matchLabels.get(row.match_id) ?? `#${row.match_id}`,
              },
              { header: "G", render: (row) => row.goals },
              { header: "A", render: (row) => row.assists },
              {
                header: "Shots",
                render: (row) =>
                  `${row.shots} (${row.shots_on_target} on target)`,
              },
              {
                header: "Rating",
                render: (row) => row.rating.toFixed(1),
              },
              {
                header: "MVP",
                render: (row) =>
                  row.mvp ? (
                    <Badge tone="green">MVP</Badge>
                  ) : (
                    <span className="text-slate-400">—</span>
                  ),
              },
              ...(canCoach
                ? [
                    {
                      header: "",
                      className: "text-right",
                      render: (row: PlayerStatistic) => (
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="secondary"
                            onClick={() => openEdit(row)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="danger"
                            onClick={() => setDeleting(row)}
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
            emptyMessage="No statistics recorded yet."
          />

          <Pagination
            total={list.total}
            skip={list.skip}
            limit={list.limit}
            onChange={list.setSkip}
          />
        </Card>
      </div>

      <Modal
        open={formOpen}
        title={editing ? "Edit record" : "Add record"}
        onClose={() => setFormOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {!editing && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Select
                label="Player"
                required
                value={form.player_id}
                onChange={(event) =>
                  setForm({
                    ...form,
                    player_id: event.target.value,
                  })
                }
              >
                <option value="" disabled>
                  Select
                </option>
                {players.map((player) => (
                  <option key={player.id} value={player.id}>
                    {player.first_name} {player.last_name}
                  </option>
                ))}
              </Select>
              <Select
                label="Match"
                required
                value={form.match_id}
                onChange={(event) =>
                  setForm({
                    ...form,
                    match_id: event.target.value,
                  })
                }
              >
                <option value="" disabled>
                  Select
                </option>
                {matches.map((match) => (
                  <option key={match.id} value={match.id}>
                    {matchLabels.get(match.id)}
                  </option>
                ))}
              </Select>
            </div>
          )}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {numberField("goals", "Goals")}
            {numberField("assists", "Assists")}
            {numberField("minutes_played", "Minutes")}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {numberField("shots", "Shots")}
            {numberField("shots_on_target", "On target")}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {numberField("passes", "Passes")}
            {numberField("successful_passes", "Successful")}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {numberField("interceptions", "Interceptions")}
            {numberField("tackles", "Tackles")}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {numberField("green_cards", "Green")}
            {numberField("yellow_cards", "Yellow")}
            {numberField("red_cards", "Red")}
          </div>

          <div className="grid grid-cols-1 items-end gap-3 sm:grid-cols-2">
            <Input
              label="Rating"
              type="number"
              min={0}
              max={10}
              step={0.1}
              value={form.rating}
              onChange={(event) =>
                setForm({ ...form, rating: event.target.value })
              }
            />
            <label className="flex items-center gap-2 pb-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.mvp}
                onChange={(event) =>
                  setForm({ ...form, mvp: event.target.checked })
                }
                className="h-4 w-4 rounded border-slate-300"
              />
              Man of the match
            </label>
          </div>

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
              {saving ? "Saving…" : "Save record"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        title="Delete record"
        message="Delete this statistics record? This cannot be undone."
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
