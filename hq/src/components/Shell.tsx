import Link from "next/link";
import { logoutAction } from "@/app/actions";
import type { Session } from "@/lib/types";

export function Shell({
  session,
  children,
}: {
  session: Session;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-full">
      <header className="border-b border-line bg-card/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <div className="flex items-center gap-6">
            <Link href="/" className="font-display text-xl tracking-tight">
              ACFO HQ
            </Link>
            <nav className="flex gap-4 text-sm text-muted">
              <Link href="/" className="hover:text-ink">
                Projects
              </Link>
              <Link href="/handover" className="hover:text-ink">
                Hand over a plan
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-muted">{session.name}</span>
            <form action={logoutAction}>
              <button type="submit" className="text-muted underline-offset-2 hover:underline">
                Sign out
              </button>
            </form>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}
