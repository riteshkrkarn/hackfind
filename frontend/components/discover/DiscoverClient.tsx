"use client";

import { useCallback, useEffect, useMemo, useState, useTransition } from "react";
import {
  listHackathons,
  runAgent,
  updateHackathonStatus,
} from "@/lib/api";
import type { AgentRunResult, Hackathon, HackathonStatus } from "@/lib/types";

const STATUS_ACTIONS: Array<{ status: HackathonStatus; label: string }> = [
  { status: "interested", label: "Interested" },
  { status: "joined", label: "Joined" },
  { status: "ignored", label: "Ignore" },
  { status: "new", label: "Reset" },
];

const KNOWN_SOURCES = [
  "seed",
  "devpost",
  "devfolio",
  "mlh",
  "hackerearth",
  "tavily",
] as const;

function daysUntil(iso: string | null): string | null {
  if (!iso) return null;
  const target = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(target.getTime())) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diff = Math.round((target.getTime() - today.getTime()) / 86_400_000);
  if (diff < 0) return "closed";
  if (diff === 0) return "today";
  return `${diff}d`;
}

function modeLabel(mode: Hackathon["mode"]) {
  if (mode === "in_person") return "In-person";
  if (mode === "remote") return "Remote";
  if (mode === "hybrid") return "Hybrid";
  return "Mode TBD";
}

export function DiscoverClient() {
  const [items, setItems] = useState<Hackathon[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<HackathonStatus | "">("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [query, setQuery] = useState("");
  const [runSummary, setRunSummary] = useState<AgentRunResult | null>(null);
  const [pending, startTransition] = useTransition();

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listHackathons({
        status: statusFilter,
        source: sourceFilter || undefined,
        q: query.trim() || undefined,
        limit: 100,
      });
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load hackathons");
    } finally {
      setLoading(false);
    }
  }, [query, sourceFilter, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  const sources = useMemo(() => {
    const values = new Set<string>([...KNOWN_SOURCES]);
    for (const item of items) values.add(item.source);
    return Array.from(values).sort();
  }, [items]);

  function onStatus(id: number, status: HackathonStatus) {
    startTransition(async () => {
      try {
        const updated = await updateHackathonStatus(id, status);
        setItems((prev) =>
          prev.map((item) => (item.id === id ? updated : item)),
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "Status update failed");
      }
    });
  }

  function onRunAgent() {
    startTransition(async () => {
      setError(null);
      try {
        const result = await runAgent();
        setRunSummary(result);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Agent run failed");
      }
    });
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-2">
          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
            Discover
          </h1>
          <p className="max-w-[52ch] text-muted text-pretty">
            Browse the rail, clip what fits, ignore the rest. Run the agent to
            pull fresh listings from configured sources.
          </p>
        </div>
        <button
          type="button"
          onClick={onRunAgent}
          disabled={pending}
          className="bg-band px-4 py-2.5 font-display text-sm font-semibold tracking-wide text-desk transition-[filter] hover:brightness-105 disabled:opacity-60"
        >
          {pending ? "Working…" : "Run agent"}
        </button>
      </div>

      <div className="flex flex-wrap gap-3 border border-rail bg-badge/40 p-3">
        <label className="flex min-w-[10rem] flex-1 flex-col gap-1 text-xs text-muted">
          Search
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Title contains…"
            className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
          />
        </label>
        <label className="flex min-w-[8rem] flex-col gap-1 text-xs text-muted">
          Status
          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value as HackathonStatus | "")
            }
            className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
          >
            <option value="">All</option>
            <option value="new">New</option>
            <option value="interested">Interested</option>
            <option value="joined">Joined</option>
            <option value="ignored">Ignored</option>
          </select>
        </label>
        <label className="flex min-w-[8rem] flex-col gap-1 text-xs text-muted">
          Source
          <select
            value={sourceFilter}
            onChange={(event) => setSourceFilter(event.target.value)}
            className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
          >
            <option value="">All</option>
            {sources.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
      </div>

      {runSummary ? (
        <p className="font-mono text-xs tracking-wide text-deep">
          Last run · fetched {runSummary.fetched} · new {runSummary.new} ·
          matched {runSummary.matched} · reminders {runSummary.reminders}
        </p>
      ) : null}

      {error ? (
        <div className="border border-deep/30 bg-badge px-4 py-3 text-sm text-ink">
          <p className="font-display font-semibold">Couldn’t load Discover</p>
          <p className="mt-1 text-muted">{error}</p>
          <p className="mt-2 text-muted">
            Is the API running at{" "}
            <code className="font-mono text-xs">
              {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8002"}
            </code>
            ?
          </p>
        </div>
      ) : null}

      {loading ? (
        <p className="text-sm text-muted">Loading hackathons…</p>
      ) : items.length === 0 ? (
        <div className="border border-rail px-5 py-8">
          <p className="font-display text-lg font-semibold text-ink">
            {statusFilter && statusFilter !== "new"
              ? `No ${statusFilter} hackathons`
              : query || sourceFilter || statusFilter
                ? "No matches for these filters"
                : "Rail is empty"}
          </p>
          <p className="mt-2 max-w-[48ch] text-sm text-muted text-pretty">
            {statusFilter === "interested" ||
            statusFilter === "joined" ||
            statusFilter === "ignored"
              ? `Everything is still “new”. Open Status → All (or New), then mark a listing as ${statusFilter} to see it here.`
              : query || sourceFilter || statusFilter
                ? "Try clearing search/source/status, or run the agent for fresh listings."
                : "Run the agent to scrape sources, or check that builtins/Tavily are enabled in the backend."}
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => {
            const countdown = daysUntil(item.apply_by);
            return (
              <li
                key={item.id}
                className="relative border border-rail bg-badge"
                style={{
                  backgroundImage:
                    "linear-gradient(165deg, rgba(255,255,255,0.28), rgba(255,255,255,0) 42%), url('/textures/badge-matte.png')",
                  backgroundSize: "cover",
                  boxShadow:
                    "0 10px 24px -16px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.35)",
                }}
              >
                <div className="absolute top-0 left-0 h-full w-1.5 bg-band" />
                <div className="space-y-4 p-4 pl-5 sm:p-5 sm:pl-6">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0 space-y-1">
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        className="font-display text-lg leading-snug font-semibold text-ink text-balance hover:underline"
                      >
                        {item.title}
                      </a>
                      <p className="font-mono text-[11px] tracking-wide text-deep uppercase">
                        {item.source}
                        {" · "}
                        {modeLabel(item.mode)}
                        {item.location ? ` · ${item.location}` : ""}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-mono text-[11px] tracking-wide text-muted uppercase">
                        Status
                      </p>
                      <p className="font-display text-sm font-semibold text-ink">
                        {item.status}
                      </p>
                      {countdown ? (
                        <p className="mt-1 font-mono text-xs text-deep tabular-nums">
                          Apply {countdown}
                        </p>
                      ) : null}
                    </div>
                  </div>

                  {item.description ? (
                    <p className="max-w-[70ch] text-sm text-muted text-pretty">
                      {item.description}
                    </p>
                  ) : null}

                  <div className="flex flex-wrap gap-2">
                    {STATUS_ACTIONS.filter(
                      (action) => action.status !== item.status,
                    ).map((action) => (
                      <button
                        key={action.status}
                        type="button"
                        disabled={pending}
                        onClick={() => onStatus(item.id, action.status)}
                        className="border border-rail px-3 py-1.5 text-xs font-medium text-ink transition-colors hover:border-ink/40 disabled:opacity-60"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
