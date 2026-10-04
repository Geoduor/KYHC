import { useState, type FormEvent } from "react";

import { DataTable, Pagination } from "../components/DataTable";
import { PageHeader } from "../components/Layout";
import { ConfirmDialog, Modal } from "../components/modal";
import {
  Badge,
  Button,
  Card,
  Input,
  Textarea,
} from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useList } from "../hooks/useList";
import { ApiError, api } from "../lib/api";
import type { Team } from "../types";

interface TeamForm {
  name: string;
  category: string;
  description: string;
  coach_name: string;
}

const EMPTY_FORM: TeamForm = {
  name: "",
  category: "",
  description: "",
  coach_name: "",
};

export default function TeamsPage() {
  const { canManage } = useAuth();

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const list = useList<Team>("/teams/", {
    search,
    category,
  });

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Team | null>(null);
  const [form, setForm] = useState<TeamForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleting, setDeleting] = useState<Team | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  function openCreate() {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setFormOpen(true);
  }

  function openEdit(team: Team) {
    setEditing(team);
    setForm({
      name: team.name,
      category: team.category,
      description: team.description ?? "",
      coach_name: team.coach_name ?? "",
    });
    setFormError(null);
    setFormOpen(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    const payload = {
      name: form.name,
      category: form.category,
      description: form.description || null,
      coach_name: form.coach_name || null,
    };

    try {
      if (editing) {
        await api.put(`/teams/${editing.id}`, payload);
      } else {
        await api.post("/teams/", payload);
      }

      setFormOpen(false);
      await list.reload();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not save team",
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
      await api.delete(`/teams/${deleting.id}`);
      setDeleting(null);
      await list.reload();
    } catch (err) {
      alert(
        err instanceof ApiError ? err.message : "Could not delete team",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Teams"
        subtitle="Squads registered with the club."
        action={
          canManage ? (
            <Button onClick={openCreate}>Add team</Button>
          ) : undefined
        }
      />

      <Card>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input
            placeholder="Search by name…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-56"
          />
          <Input
            placeholder="Filter by category…"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="w-56"
          />
        </div>

        <DataTable
          columns={[
            {
              header: "Name",
              render: (team) => (
                <span className="font-medium text-slate-800">
                  {team.name}
                </span>
              ),
            },
            {
              header: "Category",
              render: (team) => (
                <Badge tone="blue">{team.category}</Badge>
              ),
            },
            {
              header: "Coach",
              render: (team) => team.coach_name ?? "—",
            },
            {
              header: "Description",
              render: (team) => (
                <span className="text-slate-500">
                  {team.description ?? "—"}
                </span>
              ),
            },
            {
              header: "Status",
              render: (team) => (
                <Badge tone={team.is_active ? "green" : "slate"}>
                  {team.is_active ? "Active" : "Inactive"}
                </Badge>
              ),
            },
            ...(canManage
              ? [
                  {
                    header: "",
                    className: "text-right",
                    render: (team: Team) => (
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => openEdit(team)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          onClick={() => setDeleting(team)}
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
          emptyMessage="No teams yet."
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
        title={editing ? "Edit team" : "Add team"}
        onClose={() => setFormOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Name"
            required
            value={form.name}
            onChange={(event) =>
              setForm({ ...form, name: event.target.value })
            }
          />
          <Input
            label="Category"
            required
            placeholder="Youth / Senior / Veterans"
            value={form.category}
            onChange={(event) =>
              setForm({ ...form, category: event.target.value })
            }
          />
          <Input
            label="Coach name"
            value={form.coach_name}
            onChange={(event) =>
              setForm({ ...form, coach_name: event.target.value })
            }
          />
          <Textarea
            label="Description"
            rows={3}
            value={form.description}
            onChange={(event) =>
              setForm({ ...form, description: event.target.value })
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
              {saving ? "Saving…" : "Save team"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        title="Delete team"
        message={`Delete "${deleting?.name}"? This also removes its players and coaches.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
