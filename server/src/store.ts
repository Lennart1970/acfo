export interface Note {
  id: string;
  text: string;
  done: boolean;
  createdAt: string;
}

export interface CreateNoteInput {
  text: string;
}

/**
 * Tiny in-memory notes store. Persistence intentionally lives in memory so the
 * demo environment has no external database dependency; swap this for a real
 * datastore when the app grows.
 */
export class NoteStore {
  private notes = new Map<string, Note>();
  private counter = 0;

  list(): Note[] {
    return [...this.notes.values()].sort((a, b) =>
      a.createdAt < b.createdAt ? 1 : -1,
    );
  }

  get(id: string): Note | undefined {
    return this.notes.get(id);
  }

  create(input: CreateNoteInput): Note {
    const text = input.text.trim();
    if (!text) {
      throw new Error("Note text must not be empty");
    }
    this.counter += 1;
    const note: Note = {
      id: `note-${this.counter}`,
      text,
      done: false,
      createdAt: new Date().toISOString(),
    };
    this.notes.set(note.id, note);
    return note;
  }

  toggle(id: string): Note | undefined {
    const note = this.notes.get(id);
    if (!note) return undefined;
    const updated: Note = { ...note, done: !note.done };
    this.notes.set(id, updated);
    return updated;
  }

  remove(id: string): boolean {
    return this.notes.delete(id);
  }

  clear(): void {
    this.notes.clear();
    this.counter = 0;
  }
}
