"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState, useTransition } from "react";
import { listHackathons, updateHackathonStatus } from "@/lib/api";
import type { Hackathon, HackathonStatus } from "@/lib/types";

const STATUS_ACTIONS: Array<{ status: HackathonStatus; label: string }> = [
  { status: "interested", label: "Interested" },
  { status: "joined", label: "Joined" },
  { status: "ignored", label: "Ignore" },
  { status: "new", label: "Back to rail" },
];

function daysUntil(iso: string | null): { label: string; urgent: boolean } | null {
  if (!iso) return null;
  const target = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(target.getTime())) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diff = Math.round((target.getTime() - today.getTime()) / 86_400_000);
  if (diff < 0) return { label: "closed", urgent: true };
  if (diff === 0) return { label: "due today", urgent: true };
  if (diff === 1) return { label: "1 day left", urgent: true };
  return { label: `${diff} days left`, urgent: diff <= 7 };
}

function modeLabel(mode: Hackathon["mode"]) {
  if (mode === "in_person") return "In-person";
  if (mode === "remote") return "Remote";
  if (mode === "hybrid") return "Hybrid";
  return "Mode TBD";
}

function sortByDeadline(a: Hackathon, b: Hackathon) {
  if (!a.apply_by && !b.apply_by) return a.title.localeCompare(b.title);
  if (!a.apply_by) return 1;
  if (!b.apply_by) return -1;
  return a.apply_by.localeCompare(b.apply_by);
}

export function MyListClient() {
  const [items, setItems] = useState<Hackathon[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"all" | "interested" | "joined">("all");
  const [pending, startTransition] = useTransition();

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [interested, joined] = await Promise.all([
        listHackathons({ status: "interested", limit: 100 }),
        listHackathons({ status: "joined", limit: 100 }),
      ]);
      setItems([...interested, ...joined].sort(sortByDeadline));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load my list");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const visible = useMemo(() => {
    if (tab === "all") return items;
    return items.filter((item) => item.status === tab);
  }, [items, tab]);

  function onStatus(id: number, status: HackathonStatus) {
    startTransition(async () => {
      try {
        const updated = await updateHackathonStatus(id, status);
        setItems((prev) => {
          const next = prev
            .map((item) => (item.id === id ? updated : item))
            .filter(
              (item) =>
                item.status === "interested" || item.status === "joined",
            );
          return next.sort(sortByDeadline);
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Status update failed");
      }
    });
  }

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
          My list
        </h1>
        <p className="max-w-[52ch] text-muted text-pretty">
          Interested and joined hackathons, sorted by apply-by. Mark more from{" "}
          <Link href="/discover" className="text-ink underline">
            Discover
          </Link>
          .
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {(
          [
            { id: "all", label: "All clipped" },
            { id: "interested", label: "Interested" },
            { id: "joined", label: "Joined" },
          ] as const
        ).map((option) => (
          <button
            key={option.id}
            type="button"
            onClick={() => setTab(option.id)}
            className={
              tab === option.id
                ? "bg-band px-3 py-1.5 font-display text-xs font-semibold tracking-wide text-desk"
                : "border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40"
            }
          >
            {option.label}
          </button>
        ))}
      </div>

      {error ? (
        <div className="border border-deep/30 bg-badge px-4 py-3 text-sm text-ink">
          <p className="font-display font-semibold">Couldn’t load My list</p>
          <p className="mt-1 text-muted">{error}</p>
        </div>
      ) : null}

      {loading ? (
        <p className="text-sm text-muted">Loading clipped hackathons…</p>
      ) : visible.length === 0 ? (
        <div className="border border-rail px-5 py-8">
          <p className="font-display text-lg font-semibold text-ink">
            Nothing clipped yet
          </p>
          <p className="mt-2 max-w-[48ch] text-sm text-muted text-pretty">
            Open Discover and mark listings as Interested or Joined. Deadlines
            will show here once you clip them.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {visible.map((item) => {
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
                        {item.status}
                      </p>
                      {countdown ? (
                        <p
                          className={
                            countdown.urgent
                              ? "mt-1 font-display text-sm font-semibold text-deep"
                              : "mt-1 font-mono text-xs text-deep tabular-nums"
                          }
                        >
                          {countdown.label}
                        </p>
                      ) : (
                        <p className="mt-1 font-mono text-xs text-muted">
                          No deadline
                        </p>
                      )}
                      {item.apply_by ? (
                        <p className="mt-0.5 font-mono text-[11px] text-muted">
                          Apply by {item.apply_by}
                        </p>
                      ) : null}
                    </div>
                  </div>

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
