export type Role =
  | "SUPER_ADMIN"
  | "CLUB_ADMIN"
  | "COACH"
  | "ASSISTANT_COACH"
  | "TEAM_MANAGER"
  | "MEDIC"
  | "FINANCE"
  | "PLAYER";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: Role;
  is_active: boolean;
}

export interface Page<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface Team {
  id: number;
  name: string;
  category: string;
  description: string | null;
  coach_name: string | null;
  is_active: boolean;
}

export interface Player {
  id: number;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  position: string;
  jersey_number: number;
  phone: string | null;
  email: string | null;
  emergency_contact: string | null;
  medical_notes: string | null;
  team_id: number;
  is_active: boolean;
}

export interface Coach {
  id: number;
  first_name: string;
  last_name: string;
  phone: string | null;
  email: string;
  qualification: string | null;
  experience_years: number;
  team_id: number;
  is_active: boolean;
}

export interface Match {
  id: number;
  home_team_id: number;
  away_team_id: number;
  competition: string;
  venue: string;
  match_date: string;
  status: string;
  home_score: number;
  away_score: number;
  notes: string | null;
}

export type MatchEventType =
  | "GOAL"
  | "ASSIST"
  | "GREEN_CARD"
  | "YELLOW_CARD"
  | "RED_CARD"
  | "PENALTY_CORNER"
  | "PENALTY_STROKE"
  | "SAVE"
  | "SUBSTITUTION_IN"
  | "SUBSTITUTION_OUT"
  | "INJURY";

export interface MatchEvent {
  id: number;
  minute: number;
  event_type: MatchEventType;
  description: string | null;
  match_id: number;
  player_id: number;
  assisting_player_id: number | null;
}

export type AttendanceStatus =
  | "PRESENT"
  | "LATE"
  | "ABSENT"
  | "EXCUSED"
  | "INJURED"
  | "AWAY";

export interface TrainingSession {
  id: number;
  title: string;
  description: string | null;
  venue: string;
  session_date: string;
  duration_minutes: number;
  focus_area: string;
  coach_id: number;
  is_completed: boolean;
  created_at: string;
}

export interface TrainingAttendance {
  id: number;
  training_session_id: number;
  player_id: number;
  status: AttendanceStatus;
  arrival_time: string | null;
  notes: string | null;
}

export interface PlayerStatistic {
  id: number;
  player_id: number;
  match_id: number;
  goals: number;
  assists: number;
  shots: number;
  shots_on_target: number;
  passes: number;
  successful_passes: number;
  interceptions: number;
  tackles: number;
  green_cards: number;
  yellow_cards: number;
  red_cards: number;
  minutes_played: number;
  rating: number;
  mvp: boolean;
}

export interface PlayerSummary {
  player_id: number;
  player_name: string;
  goals: number;
  assists: number;
  cards: {
    green: number;
    yellow: number;
    red: number;
  };
}

export interface TeamSummary {
  team_id: number;
  team_name: string;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  goal_events: number;
  yellow_cards: number;
  red_cards: number;
}
