import { HandoverForm } from "@/components/HandoverForm";
import { getStore } from "@/lib/get-store";

export const dynamic = "force-dynamic";

export default async function HandoverPage() {
  const projects = await getStore().listProjectCards();

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-4xl">Hand over a plan</h1>
      <p className="mt-3 text-muted">
        Paste a Cursor plan, work-order list, or markdown checklist. HQ splits it into jobs,
        creates cards, and can open a Slack thread for Grok plus a Cursor Cloud Agent.
      </p>
      <div className="mt-8 rounded-2xl border border-line bg-card p-6">
        <HandoverForm
          projects={projects.map((project) => ({ slug: project.slug, name: project.name }))}
        />
      </div>
    </div>
  );
}
