import Link from "next/link";

export function LandingHeader() {
  return (
    <header className="absolute inset-x-0 top-0 z-10">
      <div className="mx-auto flex max-w-6xl items-center justify-end px-6 py-5">
        <Link
          href="/discover"
          className="font-display text-sm font-semibold text-field/80 transition-colors hover:text-band"
        >
          Skip to Discover
        </Link>
      </div>
    </header>
  );
}
