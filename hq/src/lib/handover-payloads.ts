import type { ParsedJob, Project } from "./types";

export function buildCursorPrompt(job: ParsedJob, project: Project): string {
  const lines = [
    `You are handing off an ACFO HQ job for project "${project.name}" (${project.slug}).`,
    "",
    `Job: ${job.title}`,
    "",
    job.body || "(no extra detail)",
    "",
    "Context:",
    `- GitHub PR: ${project.github_pr_url ?? "none"}`,
    `- Suggested starting ref: ${project.default_ref}`,
    `- Repo: https://github.com/Lennart1970/acfo`,
    "",
    "Rules:",
    "- Create a new cursor/* branch. Do not merge or close existing PRs unless this job explicitly says to.",
    "- Stay scoped to this job. Do not rewrite unrelated workstreams.",
    "- If credentials are missing, document what is needed instead of inventing secrets.",
  ];
  return lines.join("\n");
}

export function buildSlackParentMessage(input: {
  job: ParsedJob;
  project: Project;
  hqUrl: string;
  cursorUrl?: string | null;
  handedBy: string;
}): string {
  const bits = [
    `*ACFO HQ handover* — ${input.project.name}`,
    `*Job:* ${input.job.title}`,
    input.job.body ? `\n${input.job.body}` : "",
    "",
    `Handed over by ${input.handedBy}`,
    `HQ: ${input.hqUrl}`,
  ];
  if (input.cursorUrl) {
    bits.push(`Cursor agent: ${input.cursorUrl}`);
  }
  return bits.filter((line) => line !== "").join("\n");
}

export function buildGrokFollowup(grokUserId: string, jobTitle: string): string {
  return `<@${grokUserId}> please pick this up: ${jobTitle}. Reply in this thread with your plan, then do the work.`;
}
