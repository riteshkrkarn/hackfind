import Link from "next/link";
import { MatchRail } from "./MatchRail";
import { SOURCES, SYNTHETIC_MATCHES } from "./data";

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-desk text-field">
      <div
        aria-hidden
        className="band-edge pointer-events-none absolute inset-y-0 left-0 w-2 bg-band sm:w-2.5"
      />
      <div className="mx-auto max-w-6xl px-6 pt-16 pb-10 sm:pt-24 sm:pb-16 lg:pb-20">
        <div className="flex flex-wrap items-end justify-between gap-4 sm:gap-6">
          <h1 className="font-display text-[clamp(2.4rem,9vw,5.5rem)] leading-[0.92] font-bold tracking-[-0.03em] text-balance">
            Hackfind
          </h1>
          <p className="font-mono text-[11px] tracking-wide text-field/55 tabular-nums sm:text-xs">
            MATCHES READY · {SYNTHETIC_MATCHES.length}
          </p>
        </div>

        <h2 className="font-display mt-5 max-w-[16ch] text-[clamp(1.35rem,4.2vw,2.35rem)] leading-[1.05] font-semibold tracking-[-0.02em] text-balance sm:mt-7">
          Check in for the hackathons that fit you.
        </h2>

        <p className="mt-4 max-w-[36ch] text-base leading-relaxed text-field/80 text-pretty sm:mt-5 sm:text-lg">
          We clip only the matches that fit — then remind you before the band
          expires.
        </p>

        <div className="mt-6 flex flex-wrap items-center gap-3 sm:mt-8 sm:gap-4">
          <Link
            href="/discover"
            className="inline-flex items-center bg-band px-5 py-3 font-display text-base font-semibold tracking-wide text-desk transition-[filter] hover:brightness-105"
          >
            Get your band
          </Link>
          <p className="max-w-[28ch] text-sm text-field/65">
            Opens Discover. Sign-in comes later — your rail is waiting.
          </p>
        </div>

        <p className="mt-6 font-mono text-[10px] tracking-[0.14em] text-field/50 uppercase sm:mt-8 sm:text-[11px]">
          Scanning {SOURCES.join(" · ")}
        </p>

        <MatchRail matches={SYNTHETIC_MATCHES} />
      </div>
    </section>
  );
}
