"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { handoverPlanAction } from "@/app/actions";
import { parsePlan } from "@/lib/parse-plan";
import type { ParsedJob } from "@/lib/types";

type ProjectOption = { slug: string; name: string };

export function HandoverForm({ projects }: { projects: ProjectOption[] }) {
  const router = useRouter();
  const [markdown, setMarkdown] = useState("");
  const [planTitle, setPlanTitle] = useState("");
  const [projectSlug, setProjectSlug] = useState(projects[0]?.slug ?? "");
  const [jobs, setJobs] = useState<ParsedJob[]>([]);
  const [selected, setSelected] = useState<Record<number, boolean>>({});
  const [postSlack, setPostSlack] = useState(true);
  const [launchCursor, setLaunchCursor] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const selectedJobs = useMemo(
    () => jobs.filter((_, index) => selected[index]),
    [jobs, selected],
  );

  function onParse() {
    const parsed = parsePlan(markdown);
    setJobs(parsed);
    setSelected(Object.fromEntries(parsed.map((_, index) => [index, true])));
    setError(parsed.length === 0 ? "No jobs found in that plan." : null);
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const result = await handoverPlanAction({
      projectSlug,
      planTitle,
      markdown,
      jobs: selectedJobs,
      postSlack,
      launchCursor,
    });
    setPending(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    router.push(`/projects/${result.slug}?notice=${encodeURIComponent(result.notice)}`);
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {error ? (
        <p className="rounded-lg border border-rose/30 bg-rose/10 px-4 py-3 text-sm text-rose">
          {error}
        </p>
      ) : null}

      <label className="block">
        <span className="mb-1 block text-sm font-medium">Plan title</span>
        <input
          value={planTitle}
          onChange={(event) => setPlanTitle(event.target.value)}
          className="w-full rounded-lg border border-line bg-card px-3 py-2"
          placeholder="Week of 12 Sep — Exact sync leftovers"
        />
      </label>

      <label className="block">
        <span className="mb-1 block text-sm font-medium">Project</span>
        <select
          value={projectSlug}
          onChange={(event) => setProjectSlug(event.target.value)}
          className="w-full rounded-lg border border-line bg-card px-3 py-2"
        >
          {projects.map((project) => (
            <option key={project.slug} value={project.slug}>
              {project.name}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="mb-1 block text-sm font-medium">Paste the plan</span>
        <textarea
          value={markdown}
          onChange={(event) => setMarkdown(event.target.value)}
          rows={12}
          className="w-full rounded-lg border border-line bg-card px-3 py-2 font-mono text-sm"
          placeholder={"## Fix Railway cron\nKeep tokens in Supabase.\n\n## Seed WO-005\nAdd the Power Platform work order to the migration."}
        />
      </label>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onParse}
          className="rounded-full border border-line bg-card px-4 py-2 text-sm"
        >
          Parse into jobs
        </button>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={postSlack}
            onChange={(event) => setPostSlack(event.target.checked)}
          />
          Post Slack thread and @Grok
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={launchCursor}
            onChange={(event) => setLaunchCursor(event.target.checked)}
          />
          Launch Cursor Cloud Agent
        </label>
      </div>

      {jobs.length > 0 ? (
        <ul className="space-y-3">
          {jobs.map((job, index) => (
            <li key={`${job.title}-${index}`} className="rounded-xl border border-line bg-card p-4">
              <label className="flex items-start gap-3">
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={Boolean(selected[index])}
                  onChange={(event) =>
                    setSelected((current) => ({ ...current, [index]: event.target.checked }))
                  }
                />
                <span>
                  <strong className="block">{job.title}</strong>
                  {job.body ? (
                    <span className="mt-1 block whitespace-pre-wrap text-sm text-muted">
                      {job.body}
                    </span>
                  ) : null}
                </span>
              </label>
            </li>
          ))}
        </ul>
      ) : null}

      <button
        type="submit"
        disabled={pending || selectedJobs.length === 0}
        className="rounded-full bg-green px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50"
      >
        {pending ? "Handing over…" : `Hand over ${selectedJobs.length || "selected"} job${selectedJobs.length === 1 ? "" : "s"}`}
      </button>
    </form>
  );
}
