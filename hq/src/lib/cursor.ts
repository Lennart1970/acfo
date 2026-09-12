import { buildCursorPrompt } from "./handover-payloads";
import type { ParsedJob, Project } from "./types";

export type CursorLaunchResult = {
  id: string;
  url: string;
  status: string;
};

export type CursorClient = {
  launchAgent(input: {
    job: ParsedJob;
    project: Project;
  }): Promise<CursorLaunchResult>;
  getAgent(id: string): Promise<CursorLaunchResult>;
};

const API = "https://api.cursor.com/v1";

function authHeader(): string {
  const key = process.env.CURSOR_API_KEY;
  if (!key) throw new Error("CURSOR_API_KEY is not set");
  return `Basic ${Buffer.from(`${key}:`).toString("base64")}`;
}

export function cursorConfigured(): boolean {
  return Boolean(process.env.CURSOR_API_KEY);
}

export function createCursorClient(): CursorClient {
  return {
    async launchAgent({ job, project }) {
      const response = await fetch(`${API}/agents`, {
        method: "POST",
        headers: {
          Authorization: authHeader(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: { text: buildCursorPrompt(job, project) },
          name: job.title.slice(0, 100),
          repos: [
            {
              url: "https://github.com/Lennart1970/acfo",
              startingRef: project.default_ref || "main",
            },
          ],
          autoCreatePR: true,
        }),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Cursor API ${response.status}: ${text}`);
      }
      const json = (await response.json()) as {
        agent?: { id: string; url: string; status: string };
        id?: string;
        url?: string;
        status?: string;
      };
      const agent = json.agent ?? json;
      if (!agent.id || !agent.url) {
        throw new Error("Cursor API did not return an agent");
      }
      return { id: agent.id, url: agent.url, status: agent.status ?? "ACTIVE" };
    },

    async getAgent(id) {
      const response = await fetch(`${API}/agents/${id}`, {
        headers: { Authorization: authHeader() },
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Cursor API ${response.status}: ${text}`);
      }
      const json = (await response.json()) as {
        id: string;
        url: string;
        status: string;
      };
      return { id: json.id, url: json.url, status: json.status };
    },
  };
}
