import Link from "next/link";
import { notFound } from "next/navigation";
import {
  connectSlackChannelAction,
  createCommentAction,
  createMessageAction,
  createTodoAction,
  handoverExistingTodoAction,
  inviteGrokAction,
  refreshCursorStatusAction,
  updateTodoStatusAction,
} from "@/app/actions";
import { Flash } from "@/components/Flash";
import { getStore } from "@/lib/get-store";

export const dynamic = "force-dynamic";

const STATUSES = ["open", "handed_over", "in_progress", "done"] as const;

export default async function ProjectPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ notice?: string; error?: string }>;
}) {
  const { slug } = await params;
  const query = await searchParams;
  const store = getStore();
  const project = await store.getProjectBySlug(slug);
  if (!project) notFound();

  const [messages, todos, installation] = await Promise.all([
    store.listMessages(project.id),
    store.listTodos(project.id),
    store.getSlackInstallation(),
  ]);
  const handovers = await store.listHandoversForTodos(todos.map((todo) => todo.id));
  const comments = await Promise.all(
    messages.map(async (message) => ({
      messageId: message.id,
      comments: await store.listComments(message.id),
    })),
  );
  const commentsByMessage = Object.fromEntries(
    comments.map((entry) => [entry.messageId, entry.comments]),
  );
  const handoverByTodo = new Map(handovers.map((handover) => [handover.todo_id, handover]));

  return (
    <div>
      <p className="text-sm text-muted">
        <Link href="/" className="hover:text-ink">
          Projects
        </Link>{" "}
        / {project.slug}
      </p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl">{project.name}</h1>
          <p className="mt-2 max-w-2xl text-muted">{project.summary}</p>
        </div>
        {project.github_pr_url ? (
          <a
            href={project.github_pr_url}
            className="text-sm text-green underline-offset-2 hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            Open GitHub PR
          </a>
        ) : null}
      </div>

      <div className="mt-6">
        <Flash notice={query.notice} error={query.error} />
      </div>

      <div className="mt-4 grid gap-6 lg:grid-cols-3">
        <section className="rounded-2xl border border-line bg-card p-5 lg:col-span-2">
          <h2 className="font-display text-2xl">Message board</h2>
          <form action={createMessageAction} className="mt-4 space-y-3">
            <input type="hidden" name="slug" value={slug} />
            <input
              name="title"
              required
              placeholder="Subject"
              className="w-full rounded-lg border border-line px-3 py-2"
            />
            <textarea
              name="body"
              required
              rows={4}
              placeholder="Write an update for this workstream"
              className="w-full rounded-lg border border-line px-3 py-2"
            />
            <button type="submit" className="rounded-full bg-green px-4 py-2 text-sm text-white">
              Post message
            </button>
          </form>

          <ul className="mt-6 space-y-4">
            {messages.length === 0 ? (
              <li className="text-sm text-muted">No messages yet.</li>
            ) : (
              messages.map((message) => (
                <li key={message.id} className="rounded-xl border border-line p-4">
                  <h3 className="font-medium">{message.title}</h3>
                  <p className="mt-1 whitespace-pre-wrap text-sm">{message.body}</p>
                  <p className="mt-2 text-xs text-muted">
                    {message.author} · {new Date(message.created_at).toLocaleString()}
                  </p>
                  <ul className="mt-3 space-y-2 border-t border-line pt-3">
                    {(commentsByMessage[message.id] ?? []).map((comment) => (
                      <li key={comment.id} className="text-sm">
                        <span className="font-medium">{comment.author}:</span> {comment.body}
                      </li>
                    ))}
                  </ul>
                  <form action={createCommentAction} className="mt-3 flex gap-2">
                    <input type="hidden" name="slug" value={slug} />
                    <input type="hidden" name="message_id" value={message.id} />
                    <input
                      name="body"
                      required
                      placeholder="Reply"
                      className="flex-1 rounded-lg border border-line px-3 py-2 text-sm"
                    />
                    <button type="submit" className="text-sm text-green">
                      Reply
                    </button>
                  </form>
                </li>
              ))
            )}
          </ul>
        </section>

        <section className="space-y-6">
          <div className="rounded-2xl border border-line bg-card p-5">
            <h2 className="font-display text-2xl">Slack + Grok</h2>
            <p className="mt-2 text-sm text-muted">
              {installation
                ? `Connected to ${installation.team_name}.`
                : "Slack is not connected yet."}
            </p>
            {project.slack_channel_name ? (
              <p className="mt-2 text-sm">
                Channel #{project.slack_channel_name}
                {project.grok_invited ? " · Grok invited" : ""}
              </p>
            ) : null}
            <div className="mt-4 flex flex-col gap-2">
              {!installation ? (
                <a
                  href="/api/slack/oauth"
                  className="rounded-full bg-green px-4 py-2 text-center text-sm text-white"
                >
                  Add ACFO HQ to Slack
                </a>
              ) : null}
              <form action={connectSlackChannelAction}>
                <input type="hidden" name="slug" value={slug} />
                <button
                  type="submit"
                  className="w-full rounded-full border border-line px-4 py-2 text-sm"
                  disabled={!installation}
                >
                  Create #acfo-{project.slug}
                </button>
              </form>
              <form action={inviteGrokAction}>
                <input type="hidden" name="slug" value={slug} />
                <button
                  type="submit"
                  className="w-full rounded-full border border-line px-4 py-2 text-sm"
                  disabled={!project.slack_channel_id}
                >
                  Invite Grok
                </button>
              </form>
            </div>
          </div>

          <div className="rounded-2xl border border-line bg-card p-5">
            <h2 className="font-display text-2xl">To-dos</h2>
            <form action={createTodoAction} className="mt-4 space-y-2">
              <input type="hidden" name="slug" value={slug} />
              <input
                name="title"
                required
                placeholder="Job title"
                className="w-full rounded-lg border border-line px-3 py-2 text-sm"
              />
              <textarea
                name="body"
                rows={3}
                placeholder="Details"
                className="w-full rounded-lg border border-line px-3 py-2 text-sm"
              />
              <button type="submit" className="rounded-full bg-green px-4 py-2 text-sm text-white">
                Add to-do
              </button>
            </form>

            <ul className="mt-5 space-y-3">
              {todos.length === 0 ? (
                <li className="text-sm text-muted">No to-dos yet.</li>
              ) : (
                todos.map((todo) => {
                  const handover = handoverByTodo.get(todo.id);
                  return (
                    <li key={todo.id} className="rounded-xl border border-line p-3">
                      <p className="font-medium">{todo.title}</p>
                      {todo.body ? (
                        <p className="mt-1 whitespace-pre-wrap text-sm text-muted">{todo.body}</p>
                      ) : null}
                      <form action={updateTodoStatusAction} className="mt-2 flex items-center gap-2">
                        <input type="hidden" name="slug" value={slug} />
                        <input type="hidden" name="todo_id" value={todo.id} />
                        <select
                          name="status"
                          defaultValue={todo.status}
                          className="rounded border border-line bg-card px-2 py-1 text-xs"
                        >
                          {STATUSES.map((status) => (
                            <option key={status} value={status}>
                              {status.replace("_", " ")}
                            </option>
                          ))}
                        </select>
                        <button type="submit" className="text-xs text-green">
                          Save
                        </button>
                      </form>
                      {handover ? (
                        <div className="mt-2 space-y-1 text-xs text-muted">
                          {handover.slack_permalink ? (
                            <a
                              href={handover.slack_permalink}
                              className="block text-green"
                              target="_blank"
                              rel="noreferrer"
                            >
                              Slack thread
                            </a>
                          ) : null}
                          {handover.cursor_agent_url ? (
                            <a
                              href={handover.cursor_agent_url}
                              className="block text-green"
                              target="_blank"
                              rel="noreferrer"
                            >
                              Cursor {handover.cursor_status ?? "agent"}
                            </a>
                          ) : null}
                          {handover.notes ? <p>{handover.notes}</p> : null}
                          {handover.cursor_agent_id ? (
                            <form action={refreshCursorStatusAction}>
                              <input type="hidden" name="slug" value={slug} />
                              <input type="hidden" name="handover_id" value={handover.id} />
                              <input type="hidden" name="agent_id" value={handover.cursor_agent_id} />
                              <button type="submit" className="text-green">
                                Refresh Cursor status
                              </button>
                            </form>
                          ) : null}
                        </div>
                      ) : (
                        <form action={handoverExistingTodoAction} className="mt-2 space-y-2 text-xs">
                          <input type="hidden" name="slug" value={slug} />
                          <input type="hidden" name="todo_id" value={todo.id} />
                          <label className="flex items-center gap-2">
                            <input type="checkbox" name="post_slack" defaultChecked />
                            Slack + Grok
                          </label>
                          <label className="flex items-center gap-2">
                            <input type="checkbox" name="launch_cursor" defaultChecked />
                            Launch Cursor
                          </label>
                          <button type="submit" className="text-green">
                            Hand over this job
                          </button>
                        </form>
                      )}
                    </li>
                  );
                })
              )}
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
