"use client";

import {
  useCallback,
  useEffect,
  useState,
  useTransition,
  type FormEvent,
} from "react";
import {
  createFilter,
  deleteFilter,
  listFilters,
  updateFilter,
} from "@/lib/api";
import type { FilterProfile, FilterProfileInput } from "@/lib/types";

const MODE_OPTIONS = ["remote", "in_person", "hybrid"] as const;

const EMPTY_FORM: FilterProfileInput = {
  name: "",
  active: true,
  tech_stack: [],
  modes: [],
  domains: [],
  min_prize: null,
  max_prize: null,
  team_size_min: null,
  team_size_max: null,
};

function splitCsv(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

function joinCsv(values: string[]): string {
  return values.join(", ");
}

function toOptionalInt(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const parsed = Number.parseInt(trimmed, 10);
  return Number.isFinite(parsed) ? parsed : null;
}

type FormState = {
  name: string;
  active: boolean;
  techStack: string;
  domains: string;
  modes: string[];
  minPrize: string;
  maxPrize: string;
  teamMin: string;
  teamMax: string;
};

function profileToForm(profile: FilterProfileInput): FormState {
  return {
    name: profile.name,
    active: profile.active,
    techStack: joinCsv(profile.tech_stack),
    domains: joinCsv(profile.domains),
    modes: [...profile.modes],
    minPrize: profile.min_prize?.toString() ?? "",
    maxPrize: profile.max_prize?.toString() ?? "",
    teamMin: profile.team_size_min?.toString() ?? "",
    teamMax: profile.team_size_max?.toString() ?? "",
  };
}

function formToInput(form: FormState): FilterProfileInput {
  return {
    name: form.name.trim(),
    active: form.active,
    tech_stack: splitCsv(form.techStack),
    domains: splitCsv(form.domains),
    modes: form.modes,
    min_prize: toOptionalInt(form.minPrize),
    max_prize: toOptionalInt(form.maxPrize),
    team_size_min: toOptionalInt(form.teamMin),
    team_size_max: toOptionalInt(form.teamMax),
  };
}

const emptyFormState = profileToForm(EMPTY_FORM);

export function FiltersClient() {
  const [profiles, setProfiles] = useState<FilterProfile[]>([]);
  const [form, setForm] = useState<FormState>(emptyFormState);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [pending, startTransition] = useTransition();

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setProfiles(await listFilters());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load filters");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function resetForm() {
    setEditingId(null);
    setForm(emptyFormState);
  }

  function startEdit(profile: FilterProfile) {
    setEditingId(profile.id);
    setForm(profileToForm(profile));
  }

  function toggleMode(mode: string) {
    setForm((prev) => ({
      ...prev,
      modes: prev.modes.includes(mode)
        ? prev.modes.filter((value) => value !== mode)
        : [...prev.modes, mode],
    }));
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const body = formToInput(form);
    if (!body.name) {
      setError("Name is required");
      return;
    }

    startTransition(async () => {
      setError(null);
      try {
        if (editingId == null) {
          await createFilter(body);
        } else {
          await updateFilter(editingId, body);
        }
        resetForm();
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Save failed");
      }
    });
  }

  function onToggleActive(profile: FilterProfile) {
    startTransition(async () => {
      setError(null);
      try {
        await updateFilter(profile.id, {
          name: profile.name,
          active: !profile.active,
          tech_stack: profile.tech_stack,
          modes: profile.modes,
          domains: profile.domains,
          min_prize: profile.min_prize,
          max_prize: profile.max_prize,
          team_size_min: profile.team_size_min,
          team_size_max: profile.team_size_max,
        });
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Toggle failed");
      }
    });
  }

  function onDelete(id: number) {
    startTransition(async () => {
      setError(null);
      try {
        await deleteFilter(id);
        if (editingId === id) resetForm();
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Delete failed");
      }
    });
  }

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
          Filters
        </h1>
        <p className="max-w-[52ch] text-muted text-pretty">
          Saved profiles the agent uses when scoring matches. Active profiles
          narrow what gets notified.
        </p>
      </div>

      {error ? (
        <div className="border border-deep/30 bg-badge px-4 py-3 text-sm text-ink">
          <p className="font-display font-semibold">Filters error</p>
          <p className="mt-1 text-muted">{error}</p>
        </div>
      ) : null}

      <form
        onSubmit={onSubmit}
        className="space-y-4 border border-rail bg-badge/40 p-4 sm:p-5"
      >
        <div className="flex flex-wrap items-end justify-between gap-3">
          <p className="font-display text-sm font-semibold text-ink">
            {editingId == null ? "New profile" : `Editing #${editingId}`}
          </p>
          {editingId != null ? (
            <button
              type="button"
              onClick={resetForm}
              className="text-xs text-muted underline hover:text-ink"
            >
              Cancel edit
            </button>
          ) : null}
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <label className="flex flex-col gap-1 text-xs text-muted sm:col-span-2">
            Name
            <input
              required
              value={form.name}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, name: event.target.value }))
              }
              placeholder="Remote AI / ML"
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>

          <label className="flex flex-col gap-1 text-xs text-muted sm:col-span-2">
            Tech stack (comma-separated)
            <input
              value={form.techStack}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, techStack: event.target.value }))
              }
              placeholder="python, react, rust"
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>

          <label className="flex flex-col gap-1 text-xs text-muted sm:col-span-2">
            Domains (comma-separated)
            <input
              value={form.domains}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, domains: event.target.value }))
              }
              placeholder="ai, fintech, climate"
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>

          <fieldset className="sm:col-span-2">
            <legend className="mb-2 text-xs text-muted">Modes</legend>
            <div className="flex flex-wrap gap-2">
              {MODE_OPTIONS.map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => toggleMode(mode)}
                  className={
                    form.modes.includes(mode)
                      ? "bg-band px-3 py-1.5 text-xs font-semibold text-desk"
                      : "border border-rail px-3 py-1.5 text-xs text-ink hover:border-ink/40"
                  }
                >
                  {mode === "in_person" ? "In-person" : mode}
                </button>
              ))}
            </div>
          </fieldset>

          <label className="flex flex-col gap-1 text-xs text-muted">
            Min prize
            <input
              type="number"
              min={0}
              value={form.minPrize}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, minPrize: event.target.value }))
              }
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>
          <label className="flex flex-col gap-1 text-xs text-muted">
            Max prize
            <input
              type="number"
              min={0}
              value={form.maxPrize}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, maxPrize: event.target.value }))
              }
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>
          <label className="flex flex-col gap-1 text-xs text-muted">
            Team size min
            <input
              type="number"
              min={1}
              value={form.teamMin}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, teamMin: event.target.value }))
              }
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>
          <label className="flex flex-col gap-1 text-xs text-muted">
            Team size max
            <input
              type="number"
              min={1}
              value={form.teamMax}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, teamMax: event.target.value }))
              }
              className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
            />
          </label>
        </div>

        <label className="flex items-center gap-2 text-sm text-ink">
          <input
            type="checkbox"
            checked={form.active}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, active: event.target.checked }))
            }
            className="size-4 accent-[var(--color-band,#b8e000)]"
          />
          Active for agent matching
        </label>

        <button
          type="submit"
          disabled={pending}
          className="bg-band px-4 py-2.5 font-display text-sm font-semibold tracking-wide text-desk transition-[filter] hover:brightness-105 disabled:opacity-60"
        >
          {pending
            ? "Saving…"
            : editingId == null
              ? "Create profile"
              : "Save changes"}
        </button>
      </form>

      {loading ? (
        <p className="text-sm text-muted">Loading profiles…</p>
      ) : profiles.length === 0 ? (
        <div className="border border-rail px-5 py-8">
          <p className="font-display text-lg font-semibold text-ink">
            No filter profiles
          </p>
          <p className="mt-2 max-w-[48ch] text-sm text-muted text-pretty">
            Create one above. Without active profiles the agent still stores
            listings, but match scoring stays open.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {profiles.map((profile) => (
            <li
              key={profile.id}
              className="border border-rail bg-badge px-4 py-4 sm:px-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="space-y-1">
                  <p className="font-display text-lg font-semibold text-ink">
                    {profile.name}
                  </p>
                  <p className="font-mono text-[11px] tracking-wide text-deep uppercase">
                    {profile.active ? "Active" : "Paused"}
                    {profile.modes.length
                      ? ` · ${profile.modes.join(" / ")}`
                      : ""}
                  </p>
                  <p className="max-w-[60ch] text-sm text-muted">
                    {[
                      profile.tech_stack.length
                        ? `Stack: ${profile.tech_stack.join(", ")}`
                        : null,
                      profile.domains.length
                        ? `Domains: ${profile.domains.join(", ")}`
                        : null,
                      profile.min_prize != null || profile.max_prize != null
                        ? `Prize: ${profile.min_prize ?? "—"}–${profile.max_prize ?? "—"}`
                        : null,
                      profile.team_size_min != null ||
                      profile.team_size_max != null
                        ? `Team: ${profile.team_size_min ?? "—"}–${profile.team_size_max ?? "—"}`
                        : null,
                    ]
                      .filter(Boolean)
                      .join(" · ") || "No constraints set"}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => onToggleActive(profile)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    {profile.active ? "Pause" : "Activate"}
                  </button>
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => startEdit(profile)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => onDelete(profile.id)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
