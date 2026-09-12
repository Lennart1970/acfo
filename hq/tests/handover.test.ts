import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { buildCursorPrompt, buildGrokFollowup, buildSlackParentMessage } from "../src/lib/handover-payloads";
import { executeHandover, summarizeHandover } from "../src/lib/handover";
import { createFileStore } from "../src/lib/file-store";
import { SEEDED_PROJECTS } from "../src/lib/seed";
import type { CursorClient } from "../src/lib/cursor";
import type { SlackClient } from "../src/lib/slack";
import type { Project } from "../src/lib/types";

const sampleProject: Project = {
  id: "p1",
  name: "Exact sync → SQL → web",
  slug: "exact-sync",
  summary: "pipeline",
  github_pr_url: "https://github.com/Lennart1970/acfo/pull/1",
  default_ref: "cursor/exact-online-mysql-sync-4963",
  slack_channel_id: "C123",
  slack_channel_name: "acfo-exact-sync",
  grok_invited: true,
  created_at: "2026-09-12T00:00:00.000Z",
};

describe("handover payloads", () => {
  it("includes project context and no-merge rule in the Cursor prompt", () => {
    const prompt = buildCursorPrompt(
      { title: "Fix cron", body: "Store tokens in Supabase." },
      sampleProject,
    );
    expect(prompt).toContain("Fix cron");
    expect(prompt).toContain("https://github.com/Lennart1970/acfo/pull/1");
    expect(prompt).toContain("Do not merge or close existing PRs");
  });

  it("builds a Slack parent and Grok follow-up", () => {
    const parent = buildSlackParentMessage({
      job: { title: "Fix cron", body: "Store tokens." },
      project: sampleProject,
      hqUrl: "http://localhost:3000/projects/exact-sync",
      cursorUrl: "https://cursor.com/agents/bc-1",
      handedBy: "Lennart",
    });
    expect(parent).toContain("ACFO HQ handover");
    expect(parent).toContain("Cursor agent: https://cursor.com/agents/bc-1");
    expect(buildGrokFollowup("UGROK", "Fix cron")).toContain("<@UGROK>");
  });
});

describe("executeHandover", () => {
  let dataDir: string;

  beforeEach(async () => {
    dataDir = await mkdtemp(path.join(tmpdir(), "acfo-hq-"));
    process.env.HQ_DATA_FILE = path.join(dataDir, "hq.json");
  });

  afterEach(async () => {
    await rm(dataDir, { recursive: true, force: true });
    delete process.env.HQ_DATA_FILE;
  });

  it("creates job cards and records Slack + Cursor results", async () => {
    const store = createFileStore();
    const project = await store.getProjectBySlug("exact-sync");
    expect(project).not.toBeNull();
    await store.updateProject(project!.id, { slack_channel_id: "C123" });

    const slack: SlackClient = {
      createChannel: vi.fn(),
      inviteUser: vi.fn(),
      lookupUserByName: vi.fn(),
      postMessage: vi.fn()
        .mockResolvedValueOnce({ channel: "C123", ts: "1.1", permalink: "https://slack/1" })
        .mockResolvedValueOnce({ channel: "C123", ts: "1.2" }),
    };
    const cursor: CursorClient = {
      launchAgent: vi.fn().mockResolvedValue({
        id: "bc-1",
        url: "https://cursor.com/agents/bc-1",
        status: "ACTIVE",
      }),
      getAgent: vi.fn(),
    };

    const results = await executeHandover(
      {
        jobs: [{ title: "Fix cron", body: "Keep tokens in Supabase." }],
        projectSlug: "exact-sync",
        planTitle: "MVP leftovers",
        planMarkdown: "- [ ] Fix cron\nKeep tokens in Supabase.",
        postSlack: true,
        launchCursor: true,
        handedBy: { name: "Lennart", email: "lennart@acfo.local" },
        appUrl: "http://localhost:3000",
      },
      { store, slack, cursor, grokUserId: "UGROK" },
    );

    expect(results).toHaveLength(1);
    expect(results[0]?.todo.title).toBe("Fix cron");
    expect(results[0]?.todo.status).toBe("handed_over");
    expect(results[0]?.handover.slack_permalink).toBe("https://slack/1");
    expect(results[0]?.handover.cursor_agent_id).toBe("bc-1");
    expect(slack.postMessage).toHaveBeenCalledTimes(2);
    expect(cursor.launchAgent).toHaveBeenCalledOnce();
    expect(summarizeHandover(results)).toBe("Handed over 1 job.");
  });

  it("skips Slack and Cursor when clients are missing", async () => {
    const store = createFileStore();
    const results = await executeHandover(
      {
        jobs: [{ title: "Write README", body: "" }],
        projectSlug: SEEDED_PROJECTS[0]!.slug,
        planTitle: "Docs",
        planMarkdown: "Write README",
        postSlack: true,
        launchCursor: true,
        handedBy: { name: "Lennart", email: "lennart@acfo.local" },
        appUrl: "http://localhost:3000",
      },
      { store, slack: null, cursor: null },
    );

    expect(results[0]?.slackSkipped).toMatch(/Slack skipped/);
    expect(results[0]?.cursorSkipped).toMatch(/Cursor skipped/);
    expect(results[0]?.todo.status).toBe("handed_over");
    expect(summarizeHandover(results)).toContain("Slack skipped");
    expect(summarizeHandover(results)).toContain("Cursor skipped");
  });
});
