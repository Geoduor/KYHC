export function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatTime(value: string | null): string {
  if (!value) {
    return "—";
  }

  // "HH:MM:SS" -> "HH:MM"
  return value.slice(0, 5);
}

export function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export function roleLabel(role: string): string {
  return role
    .toLowerCase()
    .split("_")
    .map((part) => part[0]?.toUpperCase() + part.slice(1))
    .join(" ");
}

export function eventLabel(eventType: string): string {
  return roleLabel(eventType);
}

export function titleCase(value: string): string {
  return value
    .toLowerCase()
    .split(" ")
    .map((part) => part[0]?.toUpperCase() + part.slice(1))
    .join(" ");
}
