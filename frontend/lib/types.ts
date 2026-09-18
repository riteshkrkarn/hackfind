export type HackathonStatus = "new" | "interested" | "joined" | "ignored";
export type HackathonMode = "remote" | "in_person" | "hybrid" | "unknown";
export type SourceKind = "html" | "json" | "tavily";
export type NotificationChannelType =
  | "console"
  | "email"
  | "telegram"
  | "slack";

export type Hackathon = {
  id: number;
  external_id: string;
  source: string;
  title: string;
  url: string;
  description: string | null;
  mode: HackathonMode;
  location: string | null;
  starts_on: string | null;
  ends_on: string | null;
  apply_by: string | null;
  prize_amount: number | null;
  team_size_min: number | null;
  team_size_max: number | null;
  tech_stack: string[];
  domains: string[];
  status: HackathonStatus;
  first_seen_at: string;
  last_seen_at: string;
};

export type AgentRunResult = {
  fetched: number;
  new: number;
  matched: number;
  reminders: number;
  matches: Array<{
    dedupe_key: string;
    title: string;
    source: string;
    url: string;
    score: number;
  }>;
};

export type AgentStatus = {
  running: boolean;
  interval_minutes: number;
  next_run_at: string | null;
  last_run_at: string | null;
  last_run_ok: boolean | null;
  last_run_error: string | null;
  last_run_result: {
    fetched?: number;
    new?: number;
    matched?: number;
    reminders?: number;
  } | null;
};

export type FilterProfile = {
  id: number;
  name: string;
  active: boolean;
  tech_stack: string[];
  modes: string[];
  domains: string[];
  min_prize: number | null;
  max_prize: number | null;
  team_size_min: number | null;
  team_size_max: number | null;
  created_at: string;
  updated_at: string;
};

export type FilterProfileInput = {
  name: string;
  active: boolean;
  tech_stack: string[];
  modes: string[];
  domains: string[];
  min_prize: number | null;
  max_prize: number | null;
  team_size_min: number | null;
  team_size_max: number | null;
};

export type Deadline = {
  hackathon_id: number;
  title: string;
  url: string;
  status: HackathonStatus;
  apply_by: string;
  days_left: number;
};

export type NotificationChannel = {
  id: number;
  channel: NotificationChannelType | string;
  enabled: boolean;
  config: Record<string, unknown>;
  reminder_thresholds_days: number[];
  created_at: string;
  updated_at: string;
};

export type NotificationChannelInput = {
  channel: NotificationChannelType | string;
  enabled: boolean;
  config: Record<string, unknown>;
  reminder_thresholds_days: number[];
};

export type CustomSource = {
  id: number;
  name: string;
  kind: SourceKind;
  enabled: boolean;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type CustomSourceInput = {
  name: string;
  kind: SourceKind;
  enabled: boolean;
  config: Record<string, unknown>;
};
