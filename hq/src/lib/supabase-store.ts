import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { SEEDED_PROJECTS } from "./seed";
import type { Store } from "./store";
import type {
  Handover,
  Message,
  MessageComment,
  Plan,
  Project,
  ProjectCardData,
  SlackInstallation,
  Todo,
} from "./types";

function client(): SupabaseClient {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    throw new Error("Supabase is not configured");
  }
  return createClient(url, key, { auth: { persistSession: false } });
}

async function ensureSeeded(db: SupabaseClient): Promise<void> {
  const { data, error } = await db.from("hq_projects").select("id").limit(1);
  if (error) throw error;
  if (data && data.length > 0) return;
  const { error: insertError } = await db.from("hq_projects").insert(SEEDED_PROJECTS);
  if (insertError) throw insertError;
}

function requireRow<T>(data: T | null, error: { message: string } | null, label: string): T {
  if (error) throw new Error(error.message);
  if (!data) throw new Error(`${label} not found`);
  return data;
}

export function createSupabaseStore(): Store {
  const db = client();

  return {
    async listProjectCards() {
      await ensureSeeded(db);
      const { data: projects, error } = await db
        .from("hq_projects")
        .select("*")
        .order("created_at", { ascending: true });
      if (error) throw error;
      const cards: ProjectCardData[] = [];
      for (const project of (projects ?? []) as Project[]) {
        const { data: messages } = await db
          .from("hq_messages")
          .select("title, created_at")
          .eq("project_id", project.id)
          .order("created_at", { ascending: false })
          .limit(1);
        const { data: todos } = await db
          .from("hq_todos")
          .select("id, status")
          .eq("project_id", project.id);
        const openCount = (todos ?? []).filter((todo) => todo.status !== "done").length;
        const todoIds = (todos ?? []).map((todo) => todo.id);
        let lastStatus: string | null = null;
        if (todoIds.length > 0) {
          const { data: handovers } = await db
            .from("hq_handovers")
            .select("cursor_status")
            .in("todo_id", todoIds)
            .order("created_at", { ascending: false })
            .limit(1);
          lastStatus = handovers?.[0]?.cursor_status ?? null;
        }
        cards.push({
          ...project,
          open_todo_count: openCount,
          last_message: messages?.[0] ?? null,
          last_handover_status: lastStatus,
        });
      }
      return cards;
    },

    async getProjectBySlug(slug) {
      await ensureSeeded(db);
      const { data, error } = await db.from("hq_projects").select("*").eq("slug", slug).maybeSingle();
      if (error) throw error;
      return (data as Project | null) ?? null;
    },

    async getProjectById(id) {
      const { data, error } = await db.from("hq_projects").select("*").eq("id", id).maybeSingle();
      if (error) throw error;
      return (data as Project | null) ?? null;
    },

    async updateProject(id, patch) {
      const { data, error } = await db.from("hq_projects").update(patch).eq("id", id).select("*").single();
      return requireRow(data as Project | null, error, "Project");
    },

    async listMessages(projectId) {
      const { data, error } = await db
        .from("hq_messages")
        .select("*")
        .eq("project_id", projectId)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []) as Message[];
    },

    async createMessage(input) {
      const { data, error } = await db.from("hq_messages").insert(input).select("*").single();
      return requireRow(data as Message | null, error, "Message");
    },

    async listComments(messageId) {
      const { data, error } = await db
        .from("hq_message_comments")
        .select("*")
        .eq("message_id", messageId)
        .order("created_at", { ascending: true });
      if (error) throw error;
      return (data ?? []) as MessageComment[];
    },

    async createComment(input) {
      const { data, error } = await db.from("hq_message_comments").insert(input).select("*").single();
      return requireRow(data as MessageComment | null, error, "Comment");
    },

    async listTodos(projectId) {
      const { data, error } = await db
        .from("hq_todos")
        .select("*")
        .eq("project_id", projectId)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []) as Todo[];
    },

    async getTodo(id) {
      const { data, error } = await db.from("hq_todos").select("*").eq("id", id).maybeSingle();
      if (error) throw error;
      return (data as Todo | null) ?? null;
    },

    async createTodo(input) {
      const { data, error } = await db
        .from("hq_todos")
        .insert({
          project_id: input.project_id,
          title: input.title,
          body: input.body,
          status: input.status ?? "open",
          source_plan_id: input.source_plan_id ?? null,
        })
        .select("*")
        .single();
      return requireRow(data as Todo | null, error, "Todo");
    },

    async updateTodo(id, patch) {
      const { data, error } = await db.from("hq_todos").update(patch).eq("id", id).select("*").single();
      return requireRow(data as Todo | null, error, "Todo");
    },

    async createPlan(input) {
      const { data, error } = await db.from("hq_plans").insert(input).select("*").single();
      return requireRow(data as Plan | null, error, "Plan");
    },

    async listHandoversForTodos(todoIds) {
      if (todoIds.length === 0) return [];
      const { data, error } = await db
        .from("hq_handovers")
        .select("*")
        .in("todo_id", todoIds)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []) as Handover[];
    },

    async createHandover(input) {
      const { data, error } = await db.from("hq_handovers").insert(input).select("*").single();
      return requireRow(data as Handover | null, error, "Handover");
    },

    async updateHandover(id, patch) {
      const { data, error } = await db.from("hq_handovers").update(patch).eq("id", id).select("*").single();
      return requireRow(data as Handover | null, error, "Handover");
    },

    async getSlackInstallation() {
      const { data, error } = await db
        .from("hq_slack_installations")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return (data as SlackInstallation | null) ?? null;
    },

    async upsertSlackInstallation(input) {
      const { data, error } = await db
        .from("hq_slack_installations")
        .upsert(input, { onConflict: "team_id" })
        .select("*")
        .single();
      return requireRow(data as SlackInstallation | null, error, "Slack installation");
    },
  };
}
