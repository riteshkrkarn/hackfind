"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  useTransition,
  type FormEvent,
} from "react";
import {
  createNotificationChannel,
  createSource,
  deleteNotificationChannel,
  deleteSource,
  getAgentStatus,
  listNotificationChannels,
  listSources,
  runAgent,
  updateNotificationChannel,
  updateSource,
} from "@/lib/api";
import type {
  AgentRunResult,
  AgentStatus,
  CustomSource,
  NotificationChannel,
  NotificationChannelType,
  SourceKind,
} from "@/lib/types";

const CHANNEL_TYPES: NotificationChannelType[] = [
  "console",
  "email",
  "telegram",
  "slack",
];

const SOURCE_KINDS: SourceKind[] = ["html", "json", "tavily"];

const CHANNEL_CONFIG_HINTS: Record<NotificationChannelType, string> = {
  console: "{}",
  email: '{"to_email":"you@school.edu","sendgrid_api_key":"…","from_email":"hackfind@localhost"}',
  telegram: '{"bot_token":"…","chat_id":"…"}',
  slack: '{"webhook_url":"https://hooks.slack.com/…"}',
};

const SOURCE_CONFIG_HINTS: Record<SourceKind, string> = {
  html: '{"list_url":"https://…","link_selector":"a[href*=\\"hackathon\\"]","base_url":"https://…","max_items":30}',
  json: '{"list_url":"https://…/api","items_path":"","title_key":"title","url_key":"url","max_items":50}',
  tavily:
    '{"query":"upcoming hackathons India students","max_results":15,"include_domains":["devfolio.co"]}',
};

function parseJsonObject(raw: string, label: string): Record<string, unknown> {
  const trimmed = raw.trim();
  if (!trimmed) return {};
  let parsed: unknown;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    throw new Error(`${label} must be valid JSON`);
  }
  if (
    parsed === null ||
    typeof parsed !== "object" ||
    Array.isArray(parsed)
  ) {
    throw new Error(`${label} must be a JSON object`);
  }
  return parsed as Record<string, unknown>;
}

function parseThresholds(raw: string): number[] {
  const values = raw
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => Number.parseInt(part, 10));
  if (values.some((value) => !Number.isFinite(value))) {
    throw new Error("Reminder thresholds must be integers (e.g. 7, 1, 0)");
  }
  return values.length ? values : [7, 1, 0];
}

function formatWhen(iso: string | null): string {
  if (!iso) return "never";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString();
}

export function SettingsClient() {
  const [channels, setChannels] = useState<NotificationChannel[]>([]);
  const [sources, setSources] = useState<CustomSource[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [pending, startTransition] = useTransition();
  const [runSummary, setRunSummary] = useState<AgentRunResult | null>(null);

  const [channelType, setChannelType] =
    useState<NotificationChannelType>("console");
  const [channelConfig, setChannelConfig] = useState("{}");
  const [channelThresholds, setChannelThresholds] = useState("7, 1, 0");
  const [channelEnabled, setChannelEnabled] = useState(true);

  const [sourceName, setSourceName] = useState("");
  const [sourceKind, setSourceKind] = useState<SourceKind>("html");
  const [sourceConfig, setSourceConfig] = useState(
    SOURCE_CONFIG_HINTS.html,
  );
  const [sourceEnabled, setSourceEnabled] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [nextChannels, nextSources, nextStatus] = await Promise.all([
        listNotificationChannels(),
        listSources(),
        getAgentStatus(),
      ]);
      setChannels(nextChannels);
      setSources(nextSources);
      setAgentStatus(nextStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load settings");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const channelHint = useMemo(
    () => CHANNEL_CONFIG_HINTS[channelType],
    [channelType],
  );

  function onChannelTypeChange(value: NotificationChannelType) {
    setChannelType(value);
    setChannelConfig(CHANNEL_CONFIG_HINTS[value]);
  }

  function onSourceKindChange(value: SourceKind) {
    setSourceKind(value);
    setSourceConfig(SOURCE_CONFIG_HINTS[value]);
  }

  function onCreateChannel(event: FormEvent) {
    event.preventDefault();
    startTransition(async () => {
      setError(null);
      try {
        const config = parseJsonObject(channelConfig, "Channel config");
        const reminder_thresholds_days = parseThresholds(channelThresholds);
        await createNotificationChannel({
          channel: channelType,
          enabled: channelEnabled,
          config,
          reminder_thresholds_days,
        });
        setChannelType("console");
        setChannelConfig("{}");
        setChannelThresholds("7, 1, 0");
        setChannelEnabled(true);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Create channel failed");
      }
    });
  }

  function onToggleChannel(channel: NotificationChannel) {
    startTransition(async () => {
      setError(null);
      try {
        await updateNotificationChannel(channel.id, {
          channel: channel.channel,
          enabled: !channel.enabled,
          config: channel.config,
          reminder_thresholds_days: channel.reminder_thresholds_days,
        });
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Toggle channel failed");
      }
    });
  }

  function onDeleteChannel(id: number) {
    startTransition(async () => {
      setError(null);
      try {
        await deleteNotificationChannel(id);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Delete channel failed");
      }
    });
  }

  function onCreateSource(event: FormEvent) {
    event.preventDefault();
    startTransition(async () => {
      setError(null);
      try {
        const name = sourceName.trim();
        if (!name) throw new Error("Source name is required");
        const config = parseJsonObject(sourceConfig, "Source config");
        await createSource({
          name,
          kind: sourceKind,
          enabled: sourceEnabled,
          config,
        });
        setSourceName("");
        setSourceKind("html");
        setSourceConfig(SOURCE_CONFIG_HINTS.html);
        setSourceEnabled(true);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Create source failed");
      }
    });
  }

  function onToggleSource(source: CustomSource) {
    startTransition(async () => {
      setError(null);
      try {
        await updateSource(source.id, {
          name: source.name,
          kind: source.kind,
          enabled: !source.enabled,
          config: source.config,
        });
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Toggle source failed");
      }
    });
  }

  function onDeleteSource(id: number) {
    startTransition(async () => {
      setError(null);
      try {
        await deleteSource(id);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Delete source failed");
      }
    });
  }

  function onRunAgent() {
    startTransition(async () => {
      setError(null);
      try {
        setRunSummary(await runAgent());
        setAgentStatus(await getAgentStatus());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Agent run failed");
        try {
          setAgentStatus(await getAgentStatus());
        } catch {
          /* ignore status refresh errors */
        }
      }
    });
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-2">
          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
            Settings
          </h1>
          <p className="max-w-[52ch] text-muted text-pretty">
            Notification channels, custom sources, and a manual agent run.
            Built-ins still come from backend env.
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

      {runSummary ? (
        <p className="font-mono text-xs tracking-wide text-deep">
          Last run · fetched {runSummary.fetched} · new {runSummary.new} ·
          matched {runSummary.matched} · reminders {runSummary.reminders}
        </p>
      ) : null}

      {agentStatus ? (
        <div className="border border-rail bg-badge/40 px-4 py-4 sm:px-5">
          <p className="font-display text-sm font-semibold text-ink">
            Agent schedule
          </p>
          <dl className="mt-3 grid gap-2 font-mono text-xs tracking-wide text-deep sm:grid-cols-2">
            <div>
              <dt className="text-muted uppercase">Scheduler</dt>
              <dd className="mt-0.5 text-ink">
                {agentStatus.running ? "running" : "stopped"} · every{" "}
                {agentStatus.interval_minutes}m
              </dd>
            </div>
            <div>
              <dt className="text-muted uppercase">Next run</dt>
              <dd className="mt-0.5 text-ink">
                {formatWhen(agentStatus.next_run_at)}
              </dd>
            </div>
            <div>
              <dt className="text-muted uppercase">Last run</dt>
              <dd className="mt-0.5 text-ink">
                {formatWhen(agentStatus.last_run_at)}
                {agentStatus.last_run_ok == null
                  ? ""
                  : agentStatus.last_run_ok
                    ? " · ok"
                    : " · failed"}
              </dd>
            </div>
            <div>
              <dt className="text-muted uppercase">Last result</dt>
              <dd className="mt-0.5 text-ink">
                {agentStatus.last_run_result
                  ? `fetched ${agentStatus.last_run_result.fetched ?? 0} · new ${agentStatus.last_run_result.new ?? 0} · matched ${agentStatus.last_run_result.matched ?? 0}`
                  : "—"}
              </dd>
            </div>
          </dl>
          {agentStatus.last_run_error ? (
            <p className="mt-3 text-sm text-muted">{agentStatus.last_run_error}</p>
          ) : null}
        </div>
      ) : null}

      {error ? (
        <div className="border border-deep/30 bg-badge px-4 py-3 text-sm text-ink">
          <p className="font-display font-semibold">Settings error</p>
          <p className="mt-1 text-muted">{error}</p>
        </div>
      ) : null}

      <section className="space-y-4">
        <div className="space-y-1">
          <h2 className="font-display text-xl font-semibold text-ink">
            Notifications
          </h2>
          <p className="text-sm text-muted">
            Console logs by default when no channels are enabled. Email /
            Telegram / Slack need credentials in the config JSON.
          </p>
        </div>

        <form
          onSubmit={onCreateChannel}
          className="space-y-3 border border-rail bg-badge/40 p-4 sm:p-5"
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1 text-xs text-muted">
              Channel
              <select
                value={channelType}
                onChange={(event) =>
                  onChannelTypeChange(
                    event.target.value as NotificationChannelType,
                  )
                }
                className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
              >
                {CHANNEL_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-xs text-muted">
              Reminder days
              <input
                value={channelThresholds}
                onChange={(event) => setChannelThresholds(event.target.value)}
                placeholder="7, 1, 0"
                className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
              />
            </label>
            <label className="flex flex-col gap-1 text-xs text-muted sm:col-span-2">
              Config JSON
              <textarea
                value={channelConfig}
                onChange={(event) => setChannelConfig(event.target.value)}
                rows={3}
                spellCheck={false}
                className="border border-rail bg-field px-3 py-2 font-mono text-xs text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
              />
              <span className="text-[11px] text-muted">Hint: {channelHint}</span>
            </label>
          </div>
          <label className="flex items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={channelEnabled}
              onChange={(event) => setChannelEnabled(event.target.checked)}
              className="size-4 accent-[var(--color-band,#b8e000)]"
            />
            Enabled
          </label>
          <button
            type="submit"
            disabled={pending}
            className="border border-rail px-4 py-2 text-sm font-medium text-ink hover:border-ink/40 disabled:opacity-60"
          >
            Add channel
          </button>
        </form>

        {loading ? (
          <p className="text-sm text-muted">Loading channels…</p>
        ) : channels.length === 0 ? (
          <p className="text-sm text-muted">
            No channels yet — agent falls back to console logging.
          </p>
        ) : (
          <ul className="space-y-2">
            {channels.map((channel) => (
              <li
                key={channel.id}
                className="flex flex-wrap items-center justify-between gap-3 border border-rail bg-badge px-4 py-3"
              >
                <div>
                  <p className="font-display text-sm font-semibold text-ink">
                    {channel.channel}
                  </p>
                  <p className="font-mono text-[11px] tracking-wide text-deep uppercase">
                    {channel.enabled ? "Enabled" : "Disabled"}
                    {" · thresholds "}
                    {channel.reminder_thresholds_days.join(", ")}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => onToggleChannel(channel)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    {channel.enabled ? "Disable" : "Enable"}
                  </button>
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => onDeleteChannel(channel.id)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-4">
        <div className="space-y-1">
          <h2 className="font-display text-xl font-semibold text-ink">
            Custom sources
          </h2>
          <p className="text-sm text-muted">
            Add HTML / JSON / Tavily sources without writing scraper code.
            Built-ins (Devpost, MLH, …) stay in backend{" "}
            <code className="font-mono text-xs">ENABLED_BUILTIN_SOURCES</code>.
          </p>
        </div>

        <form
          onSubmit={onCreateSource}
          className="space-y-3 border border-rail bg-badge/40 p-4 sm:p-5"
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1 text-xs text-muted">
              Name
              <input
                required
                value={sourceName}
                onChange={(event) => setSourceName(event.target.value)}
                placeholder="unstop"
                className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
              />
            </label>
            <label className="flex flex-col gap-1 text-xs text-muted">
              Kind
              <select
                value={sourceKind}
                onChange={(event) =>
                  onSourceKindChange(event.target.value as SourceKind)
                }
                className="border border-rail bg-field px-3 py-2 text-sm text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
              >
                {SOURCE_KINDS.map((kind) => (
                  <option key={kind} value={kind}>
                    {kind}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-xs text-muted sm:col-span-2">
              Config JSON
              <textarea
                value={sourceConfig}
                onChange={(event) => setSourceConfig(event.target.value)}
                rows={4}
                spellCheck={false}
                className="border border-rail bg-field px-3 py-2 font-mono text-xs text-ink outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-deep"
              />
            </label>
          </div>
          <label className="flex items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={sourceEnabled}
              onChange={(event) => setSourceEnabled(event.target.checked)}
              className="size-4 accent-[var(--color-band,#b8e000)]"
            />
            Enabled
          </label>
          <button
            type="submit"
            disabled={pending}
            className="border border-rail px-4 py-2 text-sm font-medium text-ink hover:border-ink/40 disabled:opacity-60"
          >
            Add source
          </button>
        </form>

        {loading ? (
          <p className="text-sm text-muted">Loading sources…</p>
        ) : sources.length === 0 ? (
          <p className="text-sm text-muted">No custom sources yet.</p>
        ) : (
          <ul className="space-y-2">
            {sources.map((source) => (
              <li
                key={source.id}
                className="flex flex-wrap items-center justify-between gap-3 border border-rail bg-badge px-4 py-3"
              >
                <div>
                  <p className="font-display text-sm font-semibold text-ink">
                    {source.name}
                  </p>
                  <p className="font-mono text-[11px] tracking-wide text-deep uppercase">
                    {source.kind}
                    {" · "}
                    {source.enabled ? "Enabled" : "Disabled"}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => onToggleSource(source)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    {source.enabled ? "Disable" : "Enable"}
                  </button>
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => onDeleteSource(source.id)}
                    className="border border-rail px-3 py-1.5 text-xs font-medium text-ink hover:border-ink/40 disabled:opacity-60"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
