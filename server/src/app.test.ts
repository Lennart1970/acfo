import request from "supertest";
import { describe, expect, it } from "vitest";
import { createApp } from "./app.js";

describe("acfo API", () => {
  it("reports health", async () => {
    const app = createApp();
    const res = await request(app).get("/api/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });

  it("supports the full note lifecycle", async () => {
    const app = createApp();

    const created = await request(app)
      .post("/api/notes")
      .send({ text: "buy milk" });
    expect(created.status).toBe(201);
    const id = created.body.id as string;
    expect(created.body.text).toBe("buy milk");

    const listed = await request(app).get("/api/notes");
    expect(listed.status).toBe(200);
    expect(listed.body).toHaveLength(1);

    const toggled = await request(app).post(`/api/notes/${id}/toggle`);
    expect(toggled.status).toBe(200);
    expect(toggled.body.done).toBe(true);

    const removed = await request(app).delete(`/api/notes/${id}`);
    expect(removed.status).toBe(204);

    const empty = await request(app).get("/api/notes");
    expect(empty.body).toHaveLength(0);
  });

  it("rejects empty note text", async () => {
    const app = createApp();
    const res = await request(app).post("/api/notes").send({ text: "  " });
    expect(res.status).toBe(400);
  });
});
