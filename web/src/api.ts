export interface Note {
  id: string;
  text: string;
  done: boolean;
  createdAt: string;
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { error?: string };
    throw new Error(body.error ?? `Request failed with ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async list(): Promise<Note[]> {
    return json<Note[]>(await fetch("/api/notes"));
  },
  async create(text: string): Promise<Note> {
    return json<Note>(
      await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      }),
    );
  },
  async toggle(id: string): Promise<Note> {
    return json<Note>(
      await fetch(`/api/notes/${id}/toggle`, { method: "POST" }),
    );
  },
  async remove(id: string): Promise<void> {
    const res = await fetch(`/api/notes/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Delete failed with ${res.status}`);
  },
};
