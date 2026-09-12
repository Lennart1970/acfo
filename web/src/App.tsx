import { useEffect, useState } from "react";
import { api, type Note } from "./api.js";

export function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try {
      setNotes(await api.list());
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function addNote(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    try {
      await api.create(text);
      setText("");
      await refresh();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  const remaining = notes.filter((n) => !n.done).length;

  return (
    <main className="app">
      <header>
        <h1>acfo</h1>
        <p className="tagline">A tiny notes app running on the Cloud Agent dev environment.</p>
      </header>

      <form className="composer" onSubmit={addNote}>
        <input
          aria-label="New note"
          placeholder="What needs doing?"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p className="muted">Loading…</p>
      ) : notes.length === 0 ? (
        <p className="muted">No notes yet — add your first one above.</p>
      ) : (
        <ul className="notes">
          {notes.map((note) => (
            <li key={note.id} className={note.done ? "done" : ""}>
              <label>
                <input
                  type="checkbox"
                  checked={note.done}
                  onChange={async () => {
                    await api.toggle(note.id);
                    await refresh();
                  }}
                />
                <span>{note.text}</span>
              </label>
              <button
                className="delete"
                aria-label={`Delete ${note.text}`}
                onClick={async () => {
                  await api.remove(note.id);
                  await refresh();
                }}
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}

      <footer className="muted">
        {remaining} open · {notes.length} total
      </footer>
    </main>
  );
}
