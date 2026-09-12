import Link from "next/link";
import { Flash } from "@/components/Flash";
import { getStore } from "@/lib/get-store";

export const dynamic = "force-dynamic";

function statusLabel(project: {
  slack_channel_name: string | null;
  grok_invited: boolean;
  last_handover_status: string | null;
}) {
  if (project.last_handover_status) return `Agent ${project.last_handover_status}`;
  if (project.grok_invited) return "Grok invited";
  if (project.slack_channel_name) return `#${project.slack_channel_name}`;
  return "No Slack yet";
}

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ notice?: string; error?: string }>;
}) {
  const query = await searchParams;
  const projects = await getStore().listProjectCards();

  return (
    <div>
      <Flash notice={query.notice} error={query.error} />
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl">Projects</h1>
          <p className="mt-2 max-w-2xl text-muted">
            One HQ project per aCFO workstream. Open a card to post messages, track todos,
            connect Slack, and invite Grok.
          </p>
        </div>
        <Link
          href="/handover"
          className="rounded-full bg-green px-5 py-2.5 text-sm font-medium text-white"
        >
          Hand over a plan
        </Link>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {projects.map((project) => (
          <Link
            key={project.id}
            href={`/projects/${project.slug}`}
            className="rounded-2xl border border-line bg-card p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-green/40"
          >
            <div className="flex items-start justify-between gap-3">
              <h2 className="font-display text-2xl leading-tight">{project.name}</h2>
              <span className="rounded-full bg-paper-dark px-2.5 py-1 text-xs text-muted">
                {project.open_todo_count} open
              </span>
            </div>
            <p className="mt-3 text-sm leading-6 text-muted">{project.summary}</p>
            <div className="mt-5 flex flex-wrap items-center gap-3 text-xs text-muted">
              <span>{statusLabel(project)}</span>
              {project.last_message ? <span>Last: {project.last_message.title}</span> : null}
              {project.github_pr_url ? <span>PR linked</span> : null}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
