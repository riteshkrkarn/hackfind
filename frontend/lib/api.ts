import type {
  AgentRunResult,
  AgentStatus,
  CustomSource,
  CustomSourceInput,
  Deadline,
  FilterProfile,
  FilterProfileInput,
  Hackathon,
  HackathonStatus,
  NotificationChannel,
  NotificationChannelInput,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8002";

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`API ${response.status}: ${detail || response.statusText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export type ListHackathonsParams = {
  status?: HackathonStatus | "";
  source?: string;
  q?: string;
  limit?: number;
};

export function listHackathons(params: ListHackathonsParams = {}) {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.source) query.set("source", params.source);
  if (params.q) query.set("q", params.q);
  if (params.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return apiFetch<Hackathon[]>(`/hackathons${qs ? `?${qs}` : ""}`);
}

export function updateHackathonStatus(id: number, status: HackathonStatus) {
  return apiFetch<Hackathon>(`/hackathons/${id}/status`, {
    method: "POST",
    body: JSON.stringify({ status }),
  });
}

export function runAgent() {
  return apiFetch<AgentRunResult>("/agent/run", { method: "POST" });
}

export function getAgentStatus() {
  return apiFetch<AgentStatus>("/agent/status");
}

export function listDeadlines(limit = 50) {
  return apiFetch<Deadline[]>(`/deadlines?limit=${limit}`);
}

export function listFilters() {
  return apiFetch<FilterProfile[]>("/filters");
}

export function createFilter(body: FilterProfileInput) {
  return apiFetch<FilterProfile>("/filters", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateFilter(id: number, body: FilterProfileInput) {
  return apiFetch<FilterProfile>(`/filters/${id}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function deleteFilter(id: number) {
  return apiFetch<void>(`/filters/${id}`, { method: "DELETE" });
}

export function listNotificationChannels() {
  return apiFetch<NotificationChannel[]>("/notifications");
}

export function createNotificationChannel(body: NotificationChannelInput) {
  return apiFetch<NotificationChannel>("/notifications", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateNotificationChannel(
  id: number,
  body: NotificationChannelInput,
) {
  return apiFetch<NotificationChannel>(`/notifications/${id}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function deleteNotificationChannel(id: number) {
  return apiFetch<void>(`/notifications/${id}`, { method: "DELETE" });
}

export function listSources() {
  return apiFetch<CustomSource[]>("/sources");
}

export function createSource(body: CustomSourceInput) {
  return apiFetch<CustomSource>("/sources", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateSource(id: number, body: CustomSourceInput) {
  return apiFetch<CustomSource>(`/sources/${id}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function deleteSource(id: number) {
  return apiFetch<void>(`/sources/${id}`, { method: "DELETE" });
}
