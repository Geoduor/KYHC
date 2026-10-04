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
  Textarea,
} from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useList } from "../hooks/useList";
import { ApiError, api } from "../lib/api";
import { formatDateTime, formatTime } from "../lib/format";
import type {
  AttendanceStatus,
  Coach,
  Player,
  TrainingAttendance,
  TrainingSession,
} from "../types";

interface SessionForm {
  title: string;
  description: string;
  venue: string;
  session_date: string;
  duration_minutes: string;
  focus_area: string;
  coach_id: string;
}

const EMPTY_SESSION: SessionForm = {
  title: "",
  description: "",
  venue: "",
  session_date: "",
  duration_minutes: "90",
  focus_area: "",
  coach_id: "",
};

const ATTENDANCE_STATUSES: AttendanceStatus[] = [
  "PRESENT",
  "LATE",
  "ABSENT",
  "EXCUSED",
  "INJURED",
  "AWAY",
];

const STATUS_TONES: Record<
  AttendanceStatus,
  "green" | "amber" | "red" | "slate" | "blue"
> = {
  PRESENT: "green",
  LATE: "amber",
  ABSENT: "red",
  EXCUSED: "blue",
  INJURED: "red",
  AWAY: "slate",
};

export default function TrainingPage() {
  const { canCoach } = useAuth();

  const [tab, setTab] = useState<"sessions" | "attendance">("sessions");

  const [coachFilter, setCoachFilter] = useState("");
  const [completedFilter, setCompletedFilter] = useState("");

  const sessions = useList<TrainingSession>("/training-sessions/", {
    coach_id: coachFilter,
    is_completed: completedFilter,
  });

  const [attendanceSessionFilter, setAttendanceSessionFilter] =
    useState("");

  const attendance = useList<TrainingAttendance>(
    "/training-attendance/",
    {
      training_session_id: attendanceSessionFilter,
    },
  );

  const [coaches, setCoaches] = useState<Coach[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [allSessions, setAllSessions] = useState<TrainingSession[]>([]);

  useEffect(() => {
    api
      .get<{ items: Coach[] }>("/coaches/?limit=200")
      .then((page) => setCoaches(page.items))
      .catch(() => setCoaches([]));

    api
      .get<{ items: Player[] }>("/players/?limit=200")
      .then((page) => setPlayers(page.items))
      .catch(() => setPlayers([]));

    api
      .get<{ items: TrainingSession[] }>(
        "/training-sessions/?limit=200",
      )
      .then((page) => setAllSessions(page.items))
      .catch(() => setAllSessions([]));
  }, [sessions.data]);

  const coachNames = useMemo(
    () =>
      new Map(
        coaches.map((coach) => [
          coach.id,
          `${coach.first_name} ${coach.last_name}`,
        ]),
      ),
    [coaches],
  );

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

  const sessionLabels = useMemo(
    () =>
      new Map(
        allSessions.map((session) => [
          session.id,
          `${session.title} (${formatDateTime(session.session_date)})`,
        ]),
      ),
    [allSessions],
  );

  // Session modal state.
  const [sessionFormOpen, setSessionFormOpen] = useState(false);
  const [editingSession, setEditingSession] =
    useState<TrainingSession | null>(null);
  const [sessionForm, setSessionForm] =
    useState<SessionForm>(EMPTY_SESSION);
  const [savingSession, setSavingSession] = useState(false);
  const [sessionFormError, setSessionFormError] = useState<
    string | null
  >(null);

  // Deletion state.
  const [deletingSession, setDeletingSession] =
    useState<TrainingSession | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  // Attendance modal state.
  const [attendanceFormOpen, setAttendanceFormOpen] = useState(false);
  const [attendanceSessionId, setAttendanceSessionId] = useState("");
  const [attendancePlayerId, setAttendancePlayerId] = useState("");
  const [attendanceStatus, setAttendanceStatus] =
    useState<AttendanceStatus>("PRESENT");
  const [attendanceArrival, setAttendanceArrival] = useState("");
  const [attendanceNotes, setAttendanceNotes] = useState("");
  const [savingAttendance, setSavingAttendance] = useState(false);
  const [attendanceFormError, setAttendanceFormError] = useState<
    string | null
  >(null);

  function openCreateSession() {
    setEditingSession(null);
    setSessionForm({
      ...EMPTY_SESSION,
      coach_id: coaches[0] ? String(coaches[0].id) : "",
    });
    setSessionFormError(null);
    setSessionFormOpen(true);
  }

  function openEditSession(session: TrainingSession) {
    setEditingSession(session);
    setSessionForm({
      title: session.title,
      description: session.description ?? "",
      venue: session.venue,
      session_date: session.session_date.slice(0, 16),
      duration_minutes: String(session.duration_minutes),
      focus_area: session.focus_area,
      coach_id: String(session.coach_id),
    });
    setSessionFormError(null);
    setSessionFormOpen(true);
  }

  async function handleSessionSubmit(event: FormEvent) {
    event.preventDefault();
    setSavingSession(true);
    setSessionFormError(null);

    const payload = {
      title: sessionForm.title,
      description: sessionForm.description || null,
      venue: sessionForm.venue,
      session_date: sessionForm.session_date,
      duration_minutes: Number(sessionForm.duration_minutes),
      focus_area: sessionForm.focus_area,
      coach_id: Number(sessionForm.coach_id),
    };

    try {
      if (editingSession) {
        await api.put(
          `/training-sessions/${editingSession.id}`,
          payload,
        );
      } else {
        await api.post("/training-sessions/", payload);
      }

      setSessionFormOpen(false);
      await sessions.reload();
    } catch (err) {
      setSessionFormError(
        err instanceof ApiError
          ? err.message
          : "Could not save training session",
      );
    } finally {
      setSavingSession(false);
    }
  }

  async function toggleCompleted(session: TrainingSession) {
    try {
      await api.put(`/training-sessions/${session.id}`, {
        is_completed: !session.is_completed,
      });

      await sessions.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not update session",
      );
    }
  }

  async function handleDeleteSession() {
    if (!deletingSession) {
      return;
    }

    setDeleteBusy(true);

    try {
      await api.delete(
        `/training-sessions/${deletingSession.id}`,
      );
      setDeletingSession(null);
      await sessions.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not delete session",
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  function openAttendanceCreate(sessionId?: number) {
    setAttendanceSessionId(
      sessionId !== undefined
        ? String(sessionId)
        : attendanceSessionFilter || (allSessions[0]
            ? String(allSessions[0].id)
            : ""),
    );
    setAttendancePlayerId(
      players[0] ? String(players[0].id) : "",
    );
    setAttendanceStatus("PRESENT");
    setAttendanceArrival("");
    setAttendanceNotes("");
    setAttendanceFormError(null);
    setAttendanceFormOpen(true);
  }

  async function handleAttendanceSubmit(event: FormEvent) {
    event.preventDefault();
    setSavingAttendance(true);
    setAttendanceFormError(null);

    try {
      await api.post("/training-attendance/", {
        training_session_id: Number(attendanceSessionId),
        player_id: Number(attendancePlayerId),
        status: attendanceStatus,
        arrival_time: attendanceArrival
          ? `${attendanceArrival}:00`
          : null,
        notes: attendanceNotes || null,
      });

      setAttendanceFormOpen(false);
      await attendance.reload();
    } catch (err) {
      setAttendanceFormError(
        err instanceof ApiError
          ? err.message
          : "Could not record attendance",
      );
    } finally {
      setSavingAttendance(false);
    }
  }

  async function updateAttendanceStatus(
    record: TrainingAttendance,
    status: AttendanceStatus,
  ) {
    try {
      await api.put(`/training-attendance/${record.id}`, { status });

      await attendance.reload();
    } catch (err) {
      alert(
        err instanceof ApiError
          ? err.message
          : "Could not update attendance",
      );
    }
  }

  return (
    <div>
      <PageHeader
        title="Training"
        subtitle="Sessions and attendance tracking."
        action={
          canCoach ? (
            <Button
              onClick={() =>
                tab === "sessions"
                  ? openCreateSession()
                  : openAttendanceCreate()
              }
              disabled={
                tab === "sessions"
                  ? coaches.length === 0
                  : players.length === 0 ||
                    allSessions.length === 0
              }
            >
              {tab === "sessions"
                ? "Add session"
                : "Record attendance"}
            </Button>
          ) : undefined
        }
      />

      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setTab("sessions")}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
            tab === "sessions"
              ? "bg-brand-600 text-white"
              : "bg-white text-slate-600 hover:bg-slate-50"
          }`}
        >
          Sessions
        </button>
        <button
          onClick={() => setTab("attendance")}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
            tab === "attendance"
              ? "bg-brand-600 text-white"
              : "bg-white text-slate-600 hover:bg-slate-50"
          }`}
        >
          Attendance
        </button>
      </div>

      {tab === "sessions" ? (
        <Card>
          <div className="mb-4 flex flex-wrap gap-3">
            <Select
              value={coachFilter}
              onChange={(event) =>
                setCoachFilter(event.target.value)
              }
              className="w-full sm:w-56"
            >
              <option value="">All coaches</option>
              {coaches.map((coach) => (
                <option key={coach.id} value={coach.id}>
                  {coach.first_name} {coach.last_name}
                </option>
              ))}
            </Select>
            <Select
              value={completedFilter}
              onChange={(event) =>
                setCompletedFilter(event.target.value)
              }
              className="w-full sm:w-48"
            >
              <option value="">All sessions</option>
              <option value="true">Completed</option>
              <option value="false">Upcoming</option>
            </Select>
          </div>

          <DataTable
            columns={[
              {
                header: "Session",
                render: (session) => (
                  <div>
                    <p className="font-medium text-slate-800">
                      {session.title}
                    </p>
                    <p className="text-xs text-slate-500">
                      {session.focus_area}
                    </p>
                  </div>
                ),
              },
              {
                header: "When",
                render: (session) =>
                  formatDateTime(session.session_date),
              },
              {
                header: "Venue",
                render: (session) => session.venue,
              },
              {
                header: "Duration",
                render: (session) =>
                  `${session.duration_minutes} min`,
              },
              {
                header: "Coach",
                render: (session) =>
                  coachNames.get(session.coach_id) ??
                  `#${session.coach_id}`,
              },
              {
                header: "Status",
                render: (session) => (
                  <Badge
                    tone={session.is_completed ? "green" : "amber"}
                  >
                    {session.is_completed ? "Completed" : "Upcoming"}
                  </Badge>
                ),
              },
              {
                header: "",
                className: "text-right",
                render: (session) => (
                  <div className="flex justify-end gap-2">
                    {canCoach && (
                      <>
                        <Button
                          variant="secondary"
                          onClick={() => openAttendanceCreate(session.id)}
                        >
                          Attendance
                        </Button>
                        <Button
                          variant="ghost"
                          onClick={() => toggleCompleted(session)}
                        >
                          {session.is_completed
                            ? "Reopen"
                            : "Complete"}
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={() => openEditSession(session)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          onClick={() => setDeletingSession(session)}
                        >
                          Delete
                        </Button>
                      </>
                    )}
                  </div>
                ),
              },
            ]}
            rows={sessions.rows}
            loading={sessions.loading}
            error={sessions.error}
            onRetry={sessions.reload}
            emptyMessage="No training sessions yet."
          />

          <Pagination
            total={sessions.total}
            skip={sessions.skip}
            limit={sessions.limit}
            onChange={sessions.setSkip}
          />
        </Card>
      ) : (
        <Card>
          <div className="mb-4 flex flex-wrap gap-3">
            <Select
              value={attendanceSessionFilter}
              onChange={(event) =>
                setAttendanceSessionFilter(event.target.value)
              }
              className="w-full sm:w-96"
            >
              <option value="">All sessions</option>
              {allSessions.map((session) => (
                <option key={session.id} value={session.id}>
                  {session.title} —{" "}
                  {formatDateTime(session.session_date)}
                </option>
              ))}
            </Select>
          </div>

          <DataTable
            columns={[
              {
                header: "Session",
                render: (record) =>
                  sessionLabels.get(record.training_session_id) ??
                  `#${record.training_session_id}`,
              },
              {
                header: "Player",
                render: (record) =>
                  playerNames.get(record.player_id) ??
                  `#${record.player_id}`,
              },
              {
                header: "Arrival",
                render: (record) => formatTime(record.arrival_time),
              },
              {
                header: "Status",
                render: (record) =>
                  canCoach ? (
                    <Select
                      value={record.status}
                      onChange={(event) =>
                        updateAttendanceStatus(
                          record,
                          event.target.value as AttendanceStatus,
                        )
                      }
                    >
                      {ATTENDANCE_STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </Select>
                  ) : (
                    <Badge tone={STATUS_TONES[record.status]}>
                      {record.status}
                    </Badge>
                  ),
              },
              {
                header: "Notes",
                render: (record) => (
                  <span className="text-slate-500">
                    {record.notes ?? "—"}
                  </span>
                ),
              },
            ]}
            rows={attendance.rows}
            loading={attendance.loading}
            error={attendance.error}
            onRetry={attendance.reload}
            emptyMessage="No attendance records yet."
          />

          <Pagination
            total={attendance.total}
            skip={attendance.skip}
            limit={attendance.limit}
            onChange={attendance.setSkip}
          />
        </Card>
      )}

      <Modal
        open={sessionFormOpen}
        title={
          editingSession
            ? "Edit training session"
            : "Add training session"
        }
        onClose={() => setSessionFormOpen(false)}
      >
        <form onSubmit={handleSessionSubmit} className="space-y-4">
          <Input
            label="Title"
            required
            value={sessionForm.title}
            onChange={(event) =>
              setSessionForm({
                ...sessionForm,
                title: event.target.value,
              })
            }
          />

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input
              label="Date & time"
              type="datetime-local"
              required
              value={sessionForm.session_date}
              onChange={(event) =>
                setSessionForm({
                  ...sessionForm,
                  session_date: event.target.value,
                })
              }
            />
            <Input
              label="Duration (minutes)"
              type="number"
              min={1}
              required
              value={sessionForm.duration_minutes}
              onChange={(event) =>
                setSessionForm({
                  ...sessionForm,
                  duration_minutes: event.target.value,
                })
              }
            />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Input
              label="Venue"
              required
              value={sessionForm.venue}
              onChange={(event) =>
                setSessionForm({
                  ...sessionForm,
                  venue: event.target.value,
                })
              }
            />
            <Input
              label="Focus area"
              required
              placeholder="Conditioning / Tactics / Skills"
              value={sessionForm.focus_area}
              onChange={(event) =>
                setSessionForm({
                  ...sessionForm,
                  focus_area: event.target.value,
                })
              }
            />
          </div>

          <Select
            label="Coach"
            required
            value={sessionForm.coach_id}
            onChange={(event) =>
              setSessionForm({
                ...sessionForm,
                coach_id: event.target.value,
              })
            }
          >
            <option value="" disabled>
              Select a coach
            </option>
            {coaches.map((coach) => (
              <option key={coach.id} value={coach.id}>
                {coach.first_name} {coach.last_name}
              </option>
            ))}
          </Select>

          <Textarea
            label="Description"
            rows={3}
            value={sessionForm.description}
            onChange={(event) =>
              setSessionForm({
                ...sessionForm,
                description: event.target.value,
              })
            }
          />

          {sessionFormError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {sessionFormError}
            </p>
          )}

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setSessionFormOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={savingSession}>
              {savingSession ? "Saving…" : "Save session"}
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        open={attendanceFormOpen}
        title="Record attendance"
        onClose={() => setAttendanceFormOpen(false)}
      >
        <form onSubmit={handleAttendanceSubmit} className="space-y-4">
          <Select
            label="Training session"
            required
            value={attendanceSessionId}
            onChange={(event) =>
              setAttendanceSessionId(event.target.value)
            }
          >
            <option value="" disabled>
              Select a session
            </option>
            {allSessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.title} —{" "}
                {formatDateTime(session.session_date)}
              </option>
            ))}
          </Select>

          <Select
            label="Player"
            required
            value={attendancePlayerId}
            onChange={(event) =>
              setAttendancePlayerId(event.target.value)
            }
          >
            <option value="" disabled>
              Select a player
            </option>
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.first_name} {player.last_name}
              </option>
            ))}
          </Select>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Select
              label="Status"
              value={attendanceStatus}
              onChange={(event) =>
                setAttendanceStatus(
                  event.target.value as AttendanceStatus,
                )
              }
            >
              {ATTENDANCE_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </Select>
            <Input
              label="Arrival time"
              type="time"
              value={attendanceArrival}
              onChange={(event) =>
                setAttendanceArrival(event.target.value)
              }
            />
          </div>

          <Input
            label="Notes"
            value={attendanceNotes}
            onChange={(event) =>
              setAttendanceNotes(event.target.value)
            }
          />

          {attendanceFormError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {attendanceFormError}
            </p>
          )}

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setAttendanceFormOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={savingAttendance}>
              {savingAttendance ? "Saving…" : "Save attendance"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deletingSession !== null}
        title="Delete training session"
        message="Delete this session and all of its attendance records?"
        onConfirm={handleDeleteSession}
        onCancel={() => setDeletingSession(null)}
        busy={deleteBusy}
      />
    </div>
  );
}
