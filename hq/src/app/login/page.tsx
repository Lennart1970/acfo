import { demoLoginAction } from "@/app/actions";
import { demoAllowed, getSession } from "@/lib/auth";
import { Flash } from "@/components/Flash";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const session = await getSession();
  if (session) redirect("/");
  const params = await searchParams;

  return (
    <div className="flex min-h-full items-center justify-center px-6 py-16">
      <div className="w-full max-w-md rounded-2xl border border-line bg-card p-8 shadow-sm">
        <p className="text-sm uppercase tracking-[0.2em] text-muted">aCFO</p>
        <h1 className="mt-2 font-display text-3xl">HQ</h1>
        <p className="mt-3 text-muted">
          Follow the Exact, booking, and admin workstreams. Hand jobs from a plan to Slack,
          Grok, and Cursor.
        </p>
        <div className="mt-6">
          <Flash error={params.error} />
        </div>
        {demoAllowed() ? (
          <form action={demoLoginAction} className="space-y-4">
            <label className="block text-sm">
              Name
              <input
                name="name"
                required
                defaultValue="Lennart"
                className="mt-1 w-full rounded-lg border border-line px-3 py-2"
              />
            </label>
            <label className="block text-sm">
              Email
              <input
                name="email"
                type="email"
                required
                defaultValue="lennart@acfo.local"
                className="mt-1 w-full rounded-lg border border-line px-3 py-2"
              />
            </label>
            <button
              type="submit"
              className="w-full rounded-full bg-green py-2.5 text-sm font-medium text-white"
            >
              Continue in demo mode
            </button>
            <p className="text-xs text-muted">
              Demo mode stores HQ data in <code>.data/hq.json</code> until Supabase is
              configured. Slack and Cursor stay optional.
            </p>
          </form>
        ) : (
          <p className="text-sm text-muted">Demo login is disabled.</p>
        )}
      </div>
    </div>
  );
}
