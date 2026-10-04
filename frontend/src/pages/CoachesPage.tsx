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
import type { Coach, Team } from "../types";

interface CoachForm {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  qualification: string;
  experience_years: string;
  team_id: string;
}

const EMPTY_FORM: CoachForm = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  qualification: "",
  experience_years: "0",
  team_id: "",
};

export default function CoachesPage() {
  const { canManage } = useAuth();

  const [search, setSearch] = useState("");

  const list = useList<Coach>("/coaches/", { search });

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
  const [editing, setEditing] = useState<Coach | null>(null);
  const [form, setForm] = useState<CoachForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleting, setDeleting] = useState<Coach | null>(null);
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

  function openEdit(coach: Coach) {
    setEditing(coach);
    setForm({
      first_name: coach.first_name,
      last_name: coach.last_name,
      email: coach.email,
      phone: coach.phone ?? "",
      qualification: coach.qualification ?? "",
      experience_years: String(coach.experience_years),
      team_id: String(coach.team_id),
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
      email: form.email,
      phone: form.phone || null,
      qualification: form.qualification || null,
      experience_years: Number(form.experience_years) || 0,
      team_id: Number(form.team_id),
    };

    try {
      if (editing) {
        await api.put(`/coaches/${editing.id}`, payload);
      } else {
        await api.post("/coaches/", payload);
      }

      setFormOpen(false);
      await list.reload();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not save coach",
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
      await api.delete(`/coaches/${deleting.id}`);
      setDeleting(null);
      await list.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not delete coach",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Coaches"
        subtitle="Coaching staff and their teams."
        action={
          canManage ? (
            <Button onClick={openCreate} disabled={teams.length === 0}>
              Add coach
            </Button>
          ) : undefined
        }
      />

      <Card>
        <div className="mb-4">
          <Input
            placeholder="Search by name or email…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-64"
          />
        </div>

        <DataTable
          columns={[
            {
              header: "Coach",
              render: (coach) => (
                <span className="font-medium text-slate-800">
                  {coach.first_name} {coach.last_name}
                </span>
              ),
            },
            {
              header: "Email",
              render: (coach) => coach.email,
            },
            {
              header: "Team",
              render: (coach) =>
                teamNames.get(coach.team_id) ?? `#${coach.team_id}`,
            },
            {
              header: "Experience",
              render: (coach) =>
                coach.experience_years > 0
                  ? `${coach.experience_years} yrs`
                  : "—",
            },
            {
              header: "Status",
              render: (coach) => (
                <Badge tone={coach.is_active ? "green" : "slate"}>
                  {coach.is_active ? "Active" : "Inactive"}
                </Badge>
              ),
            },
            ...(canManage
              ? [
                  {
                    header: "",
                    className: "text-right",
                    render: (coach: Coach) => (
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => openEdit(coach)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          onClick={() => setDeleting(coach)}
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
          emptyMessage="No coaches yet."
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
        title={editing ? "Edit coach" : "Add coach"}
        onClose={() => setFormOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
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

          <Input
            label="Email"
            type="email"
            required
            value={form.email}
            onChange={(event) =>
              setForm({ ...form, email: event.target.value })
            }
          />

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

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Phone"
              value={form.phone}
              onChange={(event) =>
                setForm({ ...form, phone: event.target.value })
              }
            />
            <Input
              label="Experience (years)"
              type="number"
              min={0}
              value={form.experience_years}
              onChange={(event) =>
                setForm({
                  ...form,
                  experience_years: event.target.value,
                })
              }
            />
          </div>

          <Input
            label="Qualification"
            value={form.qualification}
            onChange={(event) =>
              setForm({ ...form, qualification: event.target.value })
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
              {saving ? "Saving…" : "Save coach"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        title="Delete coach"
        message={`Delete ${deleting?.first_name} ${deleting?.last_name}? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
