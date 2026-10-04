import { useState, type FormEvent } from "react";

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
import { roleLabel } from "../lib/format";
import type { Role, User } from "../types";

const ROLES: Role[] = [
  "SUPER_ADMIN",
  "CLUB_ADMIN",
  "COACH",
  "ASSISTANT_COACH",
  "TEAM_MANAGER",
  "MEDIC",
  "FINANCE",
  "PLAYER",
];

const ROLE_TONES: Record<
  Role,
  "green" | "amber" | "red" | "blue" | "slate"
> = {
  SUPER_ADMIN: "red",
  CLUB_ADMIN: "amber",
  COACH: "blue",
  ASSISTANT_COACH: "blue",
  TEAM_MANAGER: "blue",
  MEDIC: "slate",
  FINANCE: "slate",
  PLAYER: "green",
};

interface UserForm {
  full_name: string;
  email: string;
  password: string;
  role: Role;
  is_active: boolean;
}

const EMPTY_FORM: UserForm = {
  full_name: "",
  email: "",
  password: "",
  role: "PLAYER",
  is_active: true,
};

export default function UsersPage() {
  const { isAdmin } = useAuth();

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [activeFilter, setActiveFilter] = useState("");

  const list = useList<User>("/users/", {
    search,
    role: roleFilter,
    is_active: activeFilter,
  });

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [form, setForm] = useState<UserForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleting, setDeleting] = useState<User | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  if (!isAdmin) {
    return (
      <div>
        <PageHeader
          title="Users"
          subtitle="Manage staff and player accounts."
        />
        <Card>
          <p className="py-8 text-center text-sm text-slate-500">
            You do not have permission to manage users. Contact a
            club administrator.
          </p>
        </Card>
      </div>
    );
  }

  function openCreate() {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setFormOpen(true);
  }

  function openEdit(user: User) {
    setEditing(user);
    setForm({
      full_name: user.full_name,
      email: user.email,
      password: "",
      role: user.role,
      is_active: user.is_active,
    });
    setFormError(null);
    setFormOpen(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    try {
      if (editing) {
        await api.put(`/users/${editing.id}`, {
          full_name: form.full_name,
          email: form.email,
          password: form.password || undefined,
          role: form.role,
          is_active: form.is_active,
        });
      } else {
        await api.post("/users/", {
          full_name: form.full_name,
          email: form.email,
          password: form.password,
          role: form.role,
        });
      }

      setFormOpen(false);
      await list.reload();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not save user",
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
      await api.delete(`/users/${deleting.id}`);
      setDeleting(null);
      await list.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not delete user",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Users"
        subtitle="Accounts that can sign in to the system."
        action={<Button onClick={openCreate}>Add user</Button>}
      />

      <Card>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input
            placeholder="Search by name or email…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-64"
          />
          <Select
            value={roleFilter}
            onChange={(event) => setRoleFilter(event.target.value)}
            className="w-48"
          >
            <option value="">All roles</option>
            {ROLES.map((role) => (
              <option key={role} value={role}>
                {roleLabel(role)}
              </option>
            ))}
          </Select>
          <Select
            value={activeFilter}
            onChange={(event) => setActiveFilter(event.target.value)}
            className="w-40"
          >
            <option value="">Any status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </Select>
        </div>

        <DataTable
          columns={[
            {
              header: "Name",
              render: (user) => (
                <span className="font-medium text-slate-800">
                  {user.full_name}
                </span>
              ),
            },
            {
              header: "Email",
              render: (user) => user.email,
            },
            {
              header: "Role",
              render: (user) => (
                <Badge tone={ROLE_TONES[user.role]}>
                  {roleLabel(user.role)}
                </Badge>
              ),
            },
            {
              header: "Status",
              render: (user) => (
                <Badge tone={user.is_active ? "green" : "slate"}>
                  {user.is_active ? "Active" : "Inactive"}
                </Badge>
              ),
            },
            {
              header: "",
              className: "text-right",
              render: (user) => (
                <div className="flex justify-end gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => openEdit(user)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => setDeleting(user)}
                  >
                    Delete
                  </Button>
                </div>
              ),
            },
          ]}
          rows={list.rows}
          loading={list.loading}
          error={list.error}
          onRetry={list.reload}
          emptyMessage="No users found."
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
        title={editing ? "Edit user" : "Add user"}
        onClose={() => setFormOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Full name"
            required
            value={form.full_name}
            onChange={(event) =>
              setForm({ ...form, full_name: event.target.value })
            }
          />
          <Input
            label="Email"
            type="email"
            required
            value={form.email}
            onChange={(event) =>
              setForm({ ...form, email: event.target.value })
            }
          />
          <Input
            label={
              editing
                ? "New password (leave blank to keep current)"
                : "Password"
            }
            type="password"
            required={!editing}
            minLength={8}
            value={form.password}
            onChange={(event) =>
              setForm({ ...form, password: event.target.value })
            }
          />
          <Select
            label="Role"
            value={form.role}
            onChange={(event) =>
              setForm({
                ...form,
                role: event.target.value as Role,
              })
            }
          >
            {ROLES.map((role) => (
              <option key={role} value={role}>
                {roleLabel(role)}
              </option>
            ))}
          </Select>

          {editing && (
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(event) =>
                  setForm({
                    ...form,
                    is_active: event.target.checked,
                  })
                }
                className="h-4 w-4 rounded border-slate-300"
              />
              Account is active
            </label>
          )}

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
              {saving ? "Saving…" : "Save user"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        title="Delete user"
        message={`Delete ${deleting?.full_name}? They will no longer be able to sign in.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
