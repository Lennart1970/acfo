"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { appUrl, clearSession, getSession, setSession } from "@/lib/auth";
import { createCursorClient, cursorConfigured } from "@/lib/cursor";
import { executeHandover, summarizeHandover } from "@/lib/handover";
import { getStore } from "@/lib/get-store";
import { createSlackClient, resolveGrokUserId } from "@/lib/slack";
import type { ParsedJob, TodoStatus } from "@/lib/types";

async function requireSession() {
  const session = await getSession();
  if (!session) redirect("/login");
  return session;
}

export async function demoLoginAction(formData: FormData) {
  const name = String(formData.get("name") || "").trim();
  const email = String(formData.get("email") || "").trim();
  if (!name || !email) {
    redirect("/login?error=Name%20and%20email%20are%20required");
  }
  await setSession({ name, email });
  redirect("/");
}

export async function logoutAction() {
  await clearSession();
  redirect("/login");
}

export async function createMessageAction(formData: FormData) {
  const session = await requireSession();
  const slug = String(formData.get("slug") || "");
  const title = String(formData.get("title") || "").trim();
  const body = String(formData.get("body") || "").trim();
  if (!title || !body) {
    redirect(`/projects/${slug}?error=Title%20and%20body%20are%20required`);
  }
  const store = getStore();
  const project = await store.getProjectBySlug(slug);
  if (!project) redirect("/");
  await store.createMessage({
    project_id: project.id,
    author: session.name,
    title,
    body,
  });
  revalidatePath(`/projects/${slug}`);
  redirect(`/projects/${slug}?notice=Message%20posted`);
}

export async function createCommentAction(formData: FormData) {
  const session = await requireSession();
  const slug = String(formData.get("slug") || "");
  const messageId = String(formData.get("message_id") || "");
  const body = String(formData.get("body") || "").trim();
  if (!body) redirect(`/projects/${slug}?error=Comment%20cannot%20be%20empty`);
  const store = getStore();
  await store.createComment({
    message_id: messageId,
    author: session.name,
    body,
  });
  revalidatePath(`/projects/${slug}`);
  redirect(`/projects/${slug}?notice=Comment%20added`);
}

export async function createTodoAction(formData: FormData) {
  await requireSession();
  const slug = String(formData.get("slug") || "");
  const title = String(formData.get("title") || "").trim();
  const body = String(formData.get("body") || "").trim();
  if (!title) redirect(`/projects/${slug}?error=Todo%20title%20is%20required`);
  const store = getStore();
  const project = await store.getProjectBySlug(slug);
  if (!project) redirect("/");
  await store.createTodo({
    project_id: project.id,
    title,
    body,
  });
  revalidatePath(`/projects/${slug}`);
  redirect(`/projects/${slug}?notice=Todo%20added`);
}

export async function updateTodoStatusAction(formData: FormData) {
  await requireSession();
  const slug = String(formData.get("slug") || "");
  const id = String(formData.get("todo_id") || "");
  const status = String(formData.get("status") || "") as TodoStatus;
  const store = getStore();
  await store.updateTodo(id, { status });
  revalidatePath(`/projects/${slug}`);
  redirect(`/projects/${slug}`);
}

export async function connectSlackChannelAction(formData: FormData) {
  await requireSession();
  const slug = String(formData.get("slug") || "");
  const store = getStore();
  const project = await store.getProjectBySlug(slug);
  if (!project) redirect("/");
  const installation = await store.getSlackInstallation();
  if (!installation) {
    redirect(`/projects/${slug}?error=Connect%20Slack%20first`);
  }
  const slack = createSlackClient(installation.bot_token);
  try {
    const channel = await slack.createChannel(`acfo-${project.slug}`);
    await store.updateProject(project.id, {
      slack_channel_id: channel.id,
      slack_channel_name: channel.name,
    });
    revalidatePath(`/projects/${slug}`);
    redirect(`/projects/${slug}?notice=Created%20%23${channel.name}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Slack channel failed";
    redirect(`/projects/${slug}?error=${encodeURIComponent(message)}`);
  }
}

export async function inviteGrokAction(formData: FormData) {
  await requireSession();
  const slug = String(formData.get("slug") || "");
  const store = getStore();
  const project = await store.getProjectBySlug(slug);
  if (!project) redirect("/");
  if (!project.slack_channel_id) {
    redirect(`/projects/${slug}?error=Create%20a%20Slack%20channel%20first`);
  }
  const installation = await store.getSlackInstallation();
  if (!installation) {
    redirect(`/projects/${slug}?error=Connect%20Slack%20first`);
  }
  const slack = createSlackClient(installation.bot_token);
  const grokId = await resolveGrokUserId(slack);
  if (!grokId) {
    redirect(
      `/projects/${slug}?error=${encodeURIComponent("Could not find Grok. Set SLACK_GROK_USER_ID.")}`,
    );
  }
  try {
    await slack.inviteUser(project.slack_channel_id, grokId);
    await store.updateProject(project.id, { grok_invited: true });
    revalidatePath(`/projects/${slug}`);
    redirect(`/projects/${slug}?notice=Invited%20Grok`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Invite failed";
    redirect(`/projects/${slug}?error=${encodeURIComponent(message)}`);
  }
}

export async function handoverPlanAction(input: {
  projectSlug: string;
  planTitle: string;
  markdown: string;
  jobs: ParsedJob[];
  postSlack: boolean;
  launchCursor: boolean;
}): Promise<{ ok: true; notice: string; slug: string } | { ok: false; error: string }> {
  const session = await getSession();
  if (!session) return { ok: false, error: "Sign in first" };
  if (input.jobs.length === 0) return { ok: false, error: "Select at least one job" };

  const store = getStore();
  const installation = await store.getSlackInstallation();
  const slack = installation ? createSlackClient(installation.bot_token) : null;
  const cursor = cursorConfigured() ? createCursorClient() : null;

  try {
    const results = await executeHandover(
      {
        jobs: input.jobs,
        projectSlug: input.projectSlug,
        planTitle: input.planTitle,
        planMarkdown: input.markdown,
        postSlack: input.postSlack,
        launchCursor: input.launchCursor,
        handedBy: session,
        appUrl: appUrl(),
      },
      { store, slack, cursor },
    );
    revalidatePath("/");
    revalidatePath(`/projects/${input.projectSlug}`);
    return { ok: true, notice: summarizeHandover(results), slug: input.projectSlug };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Handover failed",
    };
  }
}

export async function handoverExistingTodoAction(formData: FormData) {
  const session = await requireSession();
  const slug = String(formData.get("slug") || "");
  const todoId = String(formData.get("todo_id") || "");
  const postSlack = formData.get("post_slack") === "on";
  const launchCursor = formData.get("launch_cursor") === "on";
  const store = getStore();
  const todo = await store.getTodo(todoId);
  if (!todo) redirect(`/projects/${slug}?error=Todo%20not%20found`);

  const installation = await store.getSlackInstallation();
  const slack = installation ? createSlackClient(installation.bot_token) : null;
  const cursor = cursorConfigured() ? createCursorClient() : null;

  try {
    const results = await executeHandover(
      {
        jobs: [{ title: todo.title, body: todo.body }],
        projectSlug: slug,
        planTitle: `Handover: ${todo.title}`,
        planMarkdown: `- [ ] ${todo.title}\n${todo.body}`,
        postSlack,
        launchCursor,
        handedBy: session,
        appUrl: appUrl(),
        existingTodoId: todo.id,
      },
      { store, slack, cursor },
    );
    revalidatePath(`/projects/${slug}`);
    redirect(`/projects/${slug}?notice=${encodeURIComponent(summarizeHandover(results))}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Handover failed";
    redirect(`/projects/${slug}?error=${encodeURIComponent(message)}`);
  }
}

export async function refreshCursorStatusAction(formData: FormData) {
  await requireSession();
  const slug = String(formData.get("slug") || "");
  const handoverId = String(formData.get("handover_id") || "");
  const agentId = String(formData.get("agent_id") || "");
  if (!cursorConfigured() || !agentId) {
    redirect(`/projects/${slug}?error=No%20Cursor%20agent%20to%20refresh`);
  }
  try {
    const agent = await createCursorClient().getAgent(agentId);
    const store = getStore();
    await store.updateHandover(handoverId, {
      cursor_status: agent.status,
      cursor_agent_url: agent.url,
    });
    revalidatePath(`/projects/${slug}`);
    redirect(`/projects/${slug}?notice=Cursor%20status%20updated`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Refresh failed";
    redirect(`/projects/${slug}?error=${encodeURIComponent(message)}`);
  }
}
