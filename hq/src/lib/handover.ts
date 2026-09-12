import { buildGrokFollowup, buildSlackParentMessage } from "./handover-payloads";
import { resolveGrokUserId, type SlackClient } from "./slack";
import type { CursorClient } from "./cursor";
import type { Store } from "./store";
import type { Handover, ParsedJob, Project, Session, Todo } from "./types";

export type HandoverRequest = {
  jobs: ParsedJob[];
  projectSlug: string;
  planTitle: string;
  planMarkdown: string;
  postSlack: boolean;
  launchCursor: boolean;
  handedBy: Session;
  appUrl: string;
  existingTodoId?: string;
};

export type HandoverJobResult = {
  todo: Todo;
  handover: Handover;
  slackSkipped?: string;
  cursorSkipped?: string;
  slackError?: string;
  cursorError?: string;
};

export async function executeHandover(
  request: HandoverRequest,
  deps: {
    store: Store;
    slack?: SlackClient | null;
    cursor?: CursorClient | null;
    grokUserId?: string | null;
  },
): Promise<HandoverJobResult[]> {
  if (request.jobs.length === 0) {
    throw new Error("Select at least one job");
  }

  const project = await deps.store.getProjectBySlug(request.projectSlug);
  if (!project) throw new Error("Project not found");

  const plan = await deps.store.createPlan({
    title: request.planTitle || `Plan for ${project.name}`,
    raw_markdown: request.planMarkdown,
  });

  const results: HandoverJobResult[] = [];

  for (const job of request.jobs) {
    let todo: Todo;
    if (request.existingTodoId) {
      const existing = await deps.store.getTodo(request.existingTodoId);
      if (!existing) throw new Error("Todo not found");
      todo = await deps.store.updateTodo(existing.id, {
        status: "handed_over",
        source_plan_id: plan.id,
      });
    } else {
      todo = await deps.store.createTodo({
        project_id: project.id,
        title: job.title,
        body: job.body,
        status: "handed_over",
        source_plan_id: plan.id,
      });
    }

    let slackChannel: string | null = project.slack_channel_id;
    let slackTs: string | null = null;
    let slackPermalink: string | null = null;
    let cursorId: string | null = null;
    let cursorUrl: string | null = null;
    let cursorStatus: string | null = null;
    const notes: string[] = [];
    let slackSkipped: string | undefined;
    let cursorSkipped: string | undefined;
    let slackError: string | undefined;
    let cursorError: string | undefined;

    if (request.launchCursor) {
      if (!deps.cursor) {
        cursorSkipped = "Cursor skipped (no API key).";
        notes.push(cursorSkipped);
      } else {
        try {
          const agent = await deps.cursor.launchAgent({ job, project });
          cursorId = agent.id;
          cursorUrl = agent.url;
          cursorStatus = agent.status;
        } catch (error) {
          cursorError = error instanceof Error ? error.message : "Cursor launch failed";
          notes.push(`Cursor error: ${cursorError}`);
        }
      }
    }

    if (request.postSlack) {
      if (!deps.slack) {
        slackSkipped = "Slack skipped (workspace not connected).";
        notes.push(slackSkipped);
      } else if (!project.slack_channel_id) {
        slackSkipped = "Slack skipped (no channel on this project).";
        notes.push(slackSkipped);
      } else {
        try {
          const hqUrl = `${request.appUrl}/projects/${project.slug}`;
          const parent = await deps.slack.postMessage({
            channel: project.slack_channel_id,
            text: buildSlackParentMessage({
              job,
              project,
              hqUrl,
              cursorUrl,
              handedBy: request.handedBy.name,
            }),
          });
          slackChannel = parent.channel;
          slackTs = parent.ts;
          slackPermalink = parent.permalink ?? null;

          const grokId = deps.grokUserId ?? (await resolveGrokUserId(deps.slack));
          if (grokId) {
            await deps.slack.postMessage({
              channel: parent.channel,
              text: buildGrokFollowup(grokId, job.title),
              threadTs: parent.ts,
            });
          } else {
            notes.push("Grok was not mentioned (no SLACK_GROK_USER_ID and no user named Grok).");
          }
        } catch (error) {
          slackError = error instanceof Error ? error.message : "Slack post failed";
          notes.push(`Slack error: ${slackError}`);
        }
      }
    }

    const handover = await deps.store.createHandover({
      todo_id: todo.id,
      slack_channel_id: slackChannel,
      slack_thread_ts: slackTs,
      slack_permalink: slackPermalink,
      cursor_agent_id: cursorId,
      cursor_agent_url: cursorUrl,
      cursor_status: cursorStatus,
      notes: notes.length > 0 ? notes.join(" ") : null,
    });

    results.push({
      todo,
      handover,
      slackSkipped,
      cursorSkipped,
      slackError,
      cursorError,
    });
  }

  return results;
}

export function summarizeHandover(results: HandoverJobResult[]): string {
  const n = results.length;
  const slackNotes = results
    .map((result) => result.slackSkipped || result.slackError)
    .filter(Boolean);
  const cursorNotes = results
    .map((result) => result.cursorSkipped || result.cursorError)
    .filter(Boolean);
  const parts = [`Handed over ${n} job${n === 1 ? "" : "s"}.`];
  if (slackNotes[0]) parts.push(slackNotes[0]);
  if (cursorNotes[0]) parts.push(cursorNotes[0]);
  return parts.join(" ");
}

export type { Project };
