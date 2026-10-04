import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const TITLES: Record<string, string> = {
  "/login": "Sign in — KYHC Club Management",
  "/": "Dashboard — KYHC Club Management",
  "/teams": "Teams — KYHC Club Management",
  "/players": "Players — KYHC Club Management",
  "/coaches": "Coaches — KYHC Club Management",
  "/matches": "Matches — KYHC Club Management",
  "/training": "Training — KYHC Club Management",
  "/statistics": "Statistics — KYHC Club Management",
  "/users": "Users — KYHC Club Management",
};

const DESCRIPTIONS: Record<string, string> = {
  "/login": "Sign in to KYHC Club Management.",
  "/": "Club snapshot: teams, players, coaches and upcoming KYHC fixtures.",
  "/teams": "KYHC squads and team registration.",
  "/players": "KYHC player register with positions and teams.",
  "/coaches": "KYHC coaching staff and their teams.",
  "/matches": "KYHC fixtures, results and match events.",
  "/training": "KYHC training sessions and attendance tracking.",
  "/statistics": "KYHC team and player statistics aggregates.",
  "/users": "KYHC staff and player account management.",
};

function upsertMeta(name: string, content: string) {
  let tag = document.querySelector<HTMLMetaElement>(
    `meta[name="${name}"]`,
  );

  if (!tag) {
    tag = document.createElement("meta");
    tag.setAttribute("name", name);
    document.head.appendChild(tag);
  }

  tag.setAttribute("content", content);
}

export function RouteMeta() {
  const { pathname } = useLocation();

  useEffect(() => {
    const base = pathname.endsWith("/") && pathname !== "/"
      ? pathname.slice(0, -1)
      : pathname;

    document.title =
      TITLES[base] ?? "KYHC — Kisumu Youngsters Hockey Club Management";

    upsertMeta(
      "description",
      DESCRIPTIONS[base] ??
        "Manage teams, players, coaches, fixtures, training sessions and statistics for Kisumu Youngsters Hockey Club.",
    );
  }, [pathname]);

  return null;
}
