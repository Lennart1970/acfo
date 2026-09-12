import type {
  Handover,
  Message,
  MessageComment,
  Plan,
  Project,
  ProjectCardData,
  SlackInstallation,
  Todo,
  TodoStatus,
} from "./types";

export type Store = {
  listProjectCards(): Promise<ProjectCardData[]>;
  getProjectBySlug(slug: string): Promise<Project | null>;
  getProjectById(id: string): Promise<Project | null>;
  updateProject(id: string, patch: Partial<Project>): Promise<Project>;
  listMessages(projectId: string): Promise<Message[]>;
  createMessage(input: {
    project_id: string;
    author: string;
    title: string;
    body: string;
  }): Promise<Message>;
  listComments(messageId: string): Promise<MessageComment[]>;
  createComment(input: {
    message_id: string;
    author: string;
    body: string;
  }): Promise<MessageComment>;
  listTodos(projectId: string): Promise<Todo[]>;
  getTodo(id: string): Promise<Todo | null>;
  createTodo(input: {
    project_id: string;
    title: string;
    body: string;
    status?: TodoStatus;
    source_plan_id?: string | null;
  }): Promise<Todo>;
  updateTodo(id: string, patch: Partial<Todo>): Promise<Todo>;
  createPlan(input: { title: string; raw_markdown: string }): Promise<Plan>;
  listHandoversForTodos(todoIds: string[]): Promise<Handover[]>;
  createHandover(input: Omit<Handover, "id" | "created_at">): Promise<Handover>;
  updateHandover(id: string, patch: Partial<Handover>): Promise<Handover>;
  getSlackInstallation(): Promise<SlackInstallation | null>;
  upsertSlackInstallation(input: {
    team_id: string;
    team_name: string;
    bot_token: string;
  }): Promise<SlackInstallation>;
};

export function nowIso(): string {
  return new Date().toISOString();
}

export function newId(): string {
  return crypto.randomUUID();
}

export function usesSupabase(): boolean {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY,
  );
}
