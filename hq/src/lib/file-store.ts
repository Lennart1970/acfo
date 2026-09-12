import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { SEEDED_PROJECTS } from "./seed";
import { newId, nowIso, type Store } from "./store";
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

type Db = {
  projects: Project[];
  messages: Message[];
  comments: MessageComment[];
  todos: Todo[];
  plans: Plan[];
  handovers: Handover[];
  slack_installations: SlackInstallation[];
};

function emptyDb(): Db {
  return {
    projects: SEEDED_PROJECTS.map((project) => ({
      ...project,
      id: newId(),
      created_at: nowIso(),
    })),
    messages: [],
    comments: [],
    todos: [],
    plans: [],
    handovers: [],
    slack_installations: [],
  };
}

function dataPath(): string {
  return process.env.HQ_DATA_FILE || path.join(process.cwd(), ".data/hq.json");
}

let writeChain: Promise<unknown> = Promise.resolve();

async function withDb<T>(fn: (db: Db) => Promise<T> | T): Promise<T> {
  const run = async () => {
    const file = dataPath();
    await mkdir(path.dirname(file), { recursive: true });
    let db: Db;
    try {
      db = JSON.parse(await readFile(/*turbopackIgnore: true*/ file, "utf8")) as Db;
    } catch {
      db = emptyDb();
      await writeFile(/*turbopackIgnore: true*/ file, JSON.stringify(db, null, 2));
    }
    const result = await fn(db);
    await writeFile(/*turbopackIgnore: true*/ file, JSON.stringify(db, null, 2));
    return result;
  };

  const next = writeChain.then(run, run);
  writeChain = next.then(
    () => undefined,
    () => undefined,
  );
  return next;
}

export function createFileStore(): Store {
  return {
    async listProjectCards() {
      return withDb((db) =>
        db.projects.map((project) => {
          const messages = db.messages
            .filter((message) => message.project_id === project.id)
            .sort((a, b) => b.created_at.localeCompare(a.created_at));
          const todos = db.todos.filter((todo) => todo.project_id === project.id);
          const todoIds = new Set(todos.map((todo) => todo.id));
          const handovers = db.handovers
            .filter((handover) => todoIds.has(handover.todo_id))
            .sort((a, b) => b.created_at.localeCompare(a.created_at));
          return {
            ...project,
            open_todo_count: todos.filter((todo) => todo.status !== "done").length,
            last_message: messages[0]
              ? { title: messages[0].title, created_at: messages[0].created_at }
              : null,
            last_handover_status: handovers[0]?.cursor_status ?? null,
          } satisfies ProjectCardData;
        }),
      );
    },

    async getProjectBySlug(slug) {
      return withDb((db) => db.projects.find((project) => project.slug === slug) ?? null);
    },

    async getProjectById(id) {
      return withDb((db) => db.projects.find((project) => project.id === id) ?? null);
    },

    async updateProject(id, patch) {
      return withDb((db) => {
        const project = db.projects.find((row) => row.id === id);
        if (!project) throw new Error("Project not found");
        Object.assign(project, patch);
        return project;
      });
    },

    async listMessages(projectId) {
      return withDb((db) =>
        db.messages
          .filter((message) => message.project_id === projectId)
          .sort((a, b) => b.created_at.localeCompare(a.created_at)),
      );
    },

    async createMessage(input) {
      return withDb((db) => {
        const message: Message = { ...input, id: newId(), created_at: nowIso() };
        db.messages.push(message);
        return message;
      });
    },

    async listComments(messageId) {
      return withDb((db) =>
        db.comments
          .filter((comment) => comment.message_id === messageId)
          .sort((a, b) => a.created_at.localeCompare(b.created_at)),
      );
    },

    async createComment(input) {
      return withDb((db) => {
        const comment: MessageComment = { ...input, id: newId(), created_at: nowIso() };
        db.comments.push(comment);
        return comment;
      });
    },

    async listTodos(projectId) {
      return withDb((db) =>
        db.todos
          .filter((todo) => todo.project_id === projectId)
          .sort((a, b) => b.created_at.localeCompare(a.created_at)),
      );
    },

    async getTodo(id) {
      return withDb((db) => db.todos.find((todo) => todo.id === id) ?? null);
    },

    async createTodo(input) {
      return withDb((db) => {
        const todo: Todo = {
          id: newId(),
          project_id: input.project_id,
          title: input.title,
          body: input.body,
          status: input.status ?? "open",
          source_plan_id: input.source_plan_id ?? null,
          created_at: nowIso(),
        };
        db.todos.push(todo);
        return todo;
      });
    },

    async updateTodo(id, patch) {
      return withDb((db) => {
        const todo = db.todos.find((row) => row.id === id);
        if (!todo) throw new Error("Todo not found");
        Object.assign(todo, patch);
        return todo;
      });
    },

    async createPlan(input) {
      return withDb((db) => {
        const plan: Plan = { ...input, id: newId(), created_at: nowIso() };
        db.plans.push(plan);
        return plan;
      });
    },

    async listHandoversForTodos(todoIds) {
      const ids = new Set(todoIds);
      return withDb((db) =>
        db.handovers
          .filter((handover) => ids.has(handover.todo_id))
          .sort((a, b) => b.created_at.localeCompare(a.created_at)),
      );
    },

    async createHandover(input) {
      return withDb((db) => {
        const handover: Handover = { ...input, id: newId(), created_at: nowIso() };
        db.handovers.push(handover);
        return handover;
      });
    },

    async updateHandover(id, patch) {
      return withDb((db) => {
        const handover = db.handovers.find((row) => row.id === id);
        if (!handover) throw new Error("Handover not found");
        Object.assign(handover, patch);
        return handover;
      });
    },

    async getSlackInstallation() {
      return withDb((db) => db.slack_installations[0] ?? null);
    },

    async upsertSlackInstallation(input) {
      return withDb((db) => {
        const existing = db.slack_installations.find((row) => row.team_id === input.team_id);
        if (existing) {
          existing.team_name = input.team_name;
          existing.bot_token = input.bot_token;
          return existing;
        }
        const row: SlackInstallation = { ...input, id: newId(), created_at: nowIso() };
        db.slack_installations.push(row);
        return row;
      });
    },
  };
}
