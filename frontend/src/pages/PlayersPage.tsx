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
import { formatDate } from "../lib/format";
import type { Player, Team } from "../types";

interface PlayerForm {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  position: string;
  jersey_number: string;
  phone: string;
  email: string;
  emergency_contact: string;
  team_id: string;
}

const EMPTY_FORM: PlayerForm = {
  first_name: "",
  last_name: "",
  date_of_birth: "",
  gender: "Male",
  position: "",
  jersey_number: "",
  phone: "",
  email: "",
  emergency_contact: "",
  team_id: "",
};

export default function PlayersPage() {
  const { canManage } = useAuth();

  const [search, setSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("");

  const list = useList<Player>("/players/", {
    search,
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
  const [editing, setEditing] = useState<Player | null>(null);
  const [form, setForm] = useState<PlayerForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleting, setDeleting] = useState<Player | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  function openCreate() {
    setEditing(null);
    setForm({
      ...EMPTY_FORM,
      team_id: teams[0] ? String(teams[0].id) : "",
    });
    setFormError(null);
    setFormOpen(true);
  }

  function openEdit(player: Player) {
    setEditing(player);
    setForm({
      first_name: player.first_name,
      last_name: player.last_name,
      date_of_birth: player.date_of_birth,
      gender: player.gender,
      position: player.position,
      jersey_number: String(player.jersey_number),
      phone: player.phone ?? "",
      email: player.email ?? "",
      emergency_contact: player.emergency_contact ?? "",
      team_id: String(player.team_id),
    });
    setFormError(null);
    setFormOpen(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    const payload = {
      first_name: form.first_name,
      last_name: form.last_name,
      date_of_birth: form.date_of_birth,
      gender: form.gender,
      position: form.position,
      jersey_number: Number(form.jersey_number),
      phone: form.phone || null,
      email: form.email || null,
      emergency_contact: form.emergency_contact || null,
      team_id: Number(form.team_id),
    };

    try {
      if (editing) {
        await api.put(`/players/${editing.id}`, payload);
      } else {
        await api.post("/players/", payload);
      }

      setFormOpen(false);
      await list.reload();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not save player",
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
      await api.delete(`/players/${deleting.id}`);
      setDeleting(null);
      await list.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not delete player",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Players"
        subtitle="Everyone registered to play for the club."
        action={
          canManage ? (
            <Button onClick={openCreate} disabled={teams.length === 0}>
              Add player
            </Button>
          ) : undefined
        }
      />

      <Card>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input
            placeholder="Search by name…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-full sm:w-56"
          />
          <Select
            value={teamFilter}
            onChange={(event) => setTeamFilter(event.target.value)}
            className="w-full sm:w-56"
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
              header: "Player",
              render: (player) => (
                <span className="font-medium text-slate-800">
                  {player.first_name} {player.last_name}
                </span>
              ),
            },
            {
              header: "#",
              render: (player) => player.jersey_number,
            },
            {
              header: "Position",
              render: (player) => (
                <Badge tone="blue">{player.position}</Badge>
              ),
            },
            {
              header: "Team",
              render: (player) =>
                teamNames.get(player.team_id) ?? `#${player.team_id}`,
            },
            {
              header: "Born",
              render: (player) => formatDate(player.date_of_birth),
            },
            {
              header: "Status",
              render: (player) => (
                <Badge tone={player.is_active ? "green" : "slate"}>
                  {player.is_active ? "Active" : "Inactive"}
                </Badge>
              ),
            },
            ...(canManage
              ? [
                  {
                    header: "",
                    className: "text-right",
                    render: (player: Player) => (
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => openEdit(player)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          onClick={() => setDeleting(player)}
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
          emptyMessage="No players registered yet."
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
        title={editing ? "Edit player" : "Add player"}
        onClose={() => setFormOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input
              label="First name"
              required
              value={form.first_name}
              onChange={(event) =>
                setForm({ ...form, first_name: event.target.value })
              }
            />
            <Input
              label="Last name"
              required
              value={form.last_name}
              onChange={(event) =>
                setForm({ ...form, last_name: event.target.value })
              }
            />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input
              label="Date of birth"
              type="date"
              required
              value={form.date_of_birth}
              onChange={(event) =>
                setForm({
                  ...form,
                  date_of_birth: event.target.value,
                })
              }
            />
            <Select
              label="Gender"
              value={form.gender}
              onChange={(event) =>
                setForm({ ...form, gender: event.target.value })
              }
            >
              <option>Male</option>
              <option>Female</option>
            </Select>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input
              label="Position"
              required
              placeholder="Forward / Midfield / Defender / Goalkeeper"
              value={form.position}
              onChange={(event) =>
                setForm({ ...form, position: event.target.value })
              }
            />
            <Input
              label="Jersey number"
              type="number"
              required
              min={1}
              value={form.jersey_number}
              onChange={(event) =>
                setForm({
                  ...form,
                  jersey_number: event.target.value,
                })
              }
            />
          </div>

          <Select
            label="Team"
            required
            value={form.team_id}
            onChange={(event) =>
              setForm({ ...form, team_id: event.target.value })
            }
          >
            <option value="" disabled>
              Select a team
            </option>
            {teams.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </Select>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input
              label="Phone"
              value={form.phone}
              onChange={(event) =>
                setForm({ ...form, phone: event.target.value })
              }
            />
            <Input
              label="Email"
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm({ ...form, email: event.target.value })
              }
            />
          </div>

          <Input
            label="Emergency contact"
            value={form.emergency_contact}
            onChange={(event) =>
              setForm({
                ...form,
                emergency_contact: event.target.value,
              })
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
              {saving ? "Saving…" : "Save player"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        title="Delete player"
        message={`Delete ${deleting?.first_name} ${deleting?.last_name}? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
