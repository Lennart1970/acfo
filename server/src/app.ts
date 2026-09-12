import cors from "cors";
import express, { type Express } from "express";
import { NoteStore } from "./store.js";

export function createApp(store: NoteStore = new NoteStore()): Express {
  const app = express();
  app.use(cors());
  app.use(express.json());

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok", service: "acfo", time: new Date().toISOString() });
  });

  app.get("/api/notes", (_req, res) => {
    res.json(store.list());
  });

  app.post("/api/notes", (req, res) => {
    const text = typeof req.body?.text === "string" ? req.body.text : "";
    try {
      const note = store.create({ text });
      res.status(201).json(note);
    } catch (err) {
      res.status(400).json({ error: (err as Error).message });
    }
  });

  app.post("/api/notes/:id/toggle", (req, res) => {
    const note = store.toggle(req.params.id);
    if (!note) {
      res.status(404).json({ error: "Note not found" });
      return;
    }
    res.json(note);
  });

  app.delete("/api/notes/:id", (req, res) => {
    const removed = store.remove(req.params.id);
    if (!removed) {
      res.status(404).json({ error: "Note not found" });
      return;
    }
    res.status(204).end();
  });

  return app;
}
