import { beforeEach, describe, expect, it } from "vitest";
import { NoteStore } from "./store.js";

describe("NoteStore", () => {
  let store: NoteStore;

  beforeEach(() => {
    store = new NoteStore();
  });

  it("creates and lists notes newest first", () => {
    store.create({ text: "first" });
    store.create({ text: "second" });
    const notes = store.list();
    expect(notes).toHaveLength(2);
    expect(notes[0].text).toBe("second");
    expect(notes[1].text).toBe("first");
  });

  it("trims text and rejects empty notes", () => {
    const note = store.create({ text: "  hello  " });
    expect(note.text).toBe("hello");
    expect(() => store.create({ text: "   " })).toThrow(/must not be empty/);
  });

  it("toggles done state", () => {
    const note = store.create({ text: "task" });
    expect(note.done).toBe(false);
    const toggled = store.toggle(note.id);
    expect(toggled?.done).toBe(true);
  });

  it("removes notes", () => {
    const note = store.create({ text: "temp" });
    expect(store.remove(note.id)).toBe(true);
    expect(store.get(note.id)).toBeUndefined();
    expect(store.remove(note.id)).toBe(false);
  });
});
