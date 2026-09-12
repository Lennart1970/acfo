export type TodoStatus = "open" | "handed_over" | "in_progress" | "done";

export type Project = {
  id: string;
  name: string;
  slug: string;
  summary: string;
  github_pr_url: string | null;
  default_ref: string;
  slack_channel_id: string | null;
  slack_channel_name: string | null;
  grok_invited: boolean;
  created_at: string;
};

export type Message = {
  id: string;
  project_id: string;
  author: string;
  title: string;
  body: string;
  created_at: string;
};

export type MessageComment = {
  id: string;
  message_id: string;
  author: string;
  body: string;
  created_at: string;
};

export type Todo = {
  id: string;
  project_id: string;
  title: string;
  body: string;
  status: TodoStatus;
  source_plan_id: string | null;
  created_at: string;
};

export type Plan = {
  id: string;
  title: string;
  raw_markdown: string;
  created_at: string;
};

export type Handover = {
  id: string;
  todo_id: string;
  slack_channel_id: string | null;
  slack_thread_ts: string | null;
  slack_permalink: string | null;
  cursor_agent_id: string | null;
  cursor_agent_url: string | null;
  cursor_status: string | null;
  notes: string | null;
  created_at: string;
};

export type SlackInstallation = {
  id: string;
  team_id: string;
  team_name: string;
  bot_token: string;
  created_at: string;
};

export type Session = {
  email: string;
  name: string;
};

export type ProjectCardData = Project & {
  open_todo_count: number;
  last_message: { title: string; created_at: string } | null;
  last_handover_status: string | null;
};

export type ParsedJob = {
  title: string;
  body: string;
};
