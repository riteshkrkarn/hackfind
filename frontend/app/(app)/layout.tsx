import Link from "next/link";

const navItems = [
  { href: "/discover", label: "Discover" },
  { href: "/my-list", label: "My list" },
  { href: "/filters", label: "Filters" },
  { href: "/settings", label: "Settings" },
] as const;

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <header className="border-b border-rail bg-field">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-6 px-6 py-4">
          <Link
            href="/"
            className="font-display text-lg font-semibold tracking-tight text-ink"
          >
            Hackfind
          </Link>
          <nav className="flex flex-wrap gap-4 text-sm text-muted">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="transition-colors hover:text-ink"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
    </>
  );
}
