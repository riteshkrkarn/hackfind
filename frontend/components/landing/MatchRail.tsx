import type { MatchBadge } from "./data";

type MatchRailProps = {
  matches: MatchBadge[];
};

export function MatchRail({ matches }: MatchRailProps) {
  return (
    <div className="mt-8 sm:mt-12">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-display text-base font-semibold tracking-tight text-field sm:text-lg">
          Your check-in rail
        </h2>
        <p className="font-mono text-[10px] tracking-wide text-field/50 uppercase sm:text-[11px]">
          Synthetic demo · replace with live matches
        </p>
      </div>

      <div
        className="relative rounded-sm bg-[color-mix(in_oklab,var(--rail)_22%,transparent)] p-2.5 sm:p-4"
        style={{
          backgroundImage:
            "repeating-linear-gradient(90deg, transparent, transparent 11px, color-mix(in oklab, var(--field) 12%, transparent) 11px, color-mix(in oklab, var(--field) 12%, transparent) 12px)",
        }}
      >
        <ul className="flex gap-3 overflow-x-auto pb-1">
          {matches.map((match, index) => (
            <li
              key={match.id}
              className="rail-item relative min-w-[200px] shrink-0 sm:min-w-[220px]"
              style={{ animationDelay: `${120 + index * 90}ms` }}
            >
              <div
                aria-hidden
                className="absolute -top-1 left-4 z-[1] h-3 w-14 rounded-full bg-desk shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]"
                style={{
                  background:
                    "linear-gradient(180deg, color-mix(in oklab, var(--desk) 88%, white), var(--desk))",
                }}
              />
              <div
                aria-hidden
                className="band-edge absolute top-0 left-0 h-full w-1.5 bg-band"
                style={{ animationDelay: `${200 + index * 90}ms` }}
              />
              <article
                className="relative overflow-hidden border border-[color-mix(in_oklab,var(--desk)_12%,transparent)] text-ink"
                style={{
                  backgroundColor: "#e4e8e1",
                  backgroundImage:
                    "linear-gradient(165deg, rgba(255,255,255,0.28), rgba(255,255,255,0) 42%), url('/textures/badge-matte.png')",
                  backgroundSize: "cover",
                  boxShadow:
                    "0 12px 28px -16px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.35)",
                }}
              >
                <div className="space-y-3 p-4 pl-5">
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-display text-base leading-snug font-semibold text-balance">
                      {match.title}
                    </p>
                    <span className="font-mono text-[10px] tracking-wide text-deep uppercase">
                      {match.source}
                    </span>
                  </div>
                  <p className="text-sm text-muted">{match.mode}</p>
                  <p className="font-mono text-xs tracking-wide text-ink tabular-nums">
                    {match.deadlineLabel}{" "}
                    <span className="font-semibold text-deep">
                      {match.daysLeft}d
                    </span>
                  </p>
                </div>
              </article>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
