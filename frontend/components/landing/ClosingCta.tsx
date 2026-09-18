import Link from "next/link";

export function ClosingCta() {
  return (
    <section className="bg-desk text-field">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-16 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-[34ch]">
          <h2 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            Claim the matches already on your rail.
          </h2>
          <p className="mt-3 text-field/75 text-pretty">
            Start in Discover. Filters and reminders wait once you’re in.
          </p>
        </div>
        <Link
          href="/discover"
          className="inline-flex shrink-0 items-center self-start bg-band px-5 py-3 font-display text-base font-semibold tracking-wide text-desk transition-[filter] hover:brightness-105 sm:self-auto"
        >
          Get your band
        </Link>
      </div>
    </section>
  );
}
