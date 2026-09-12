import { describe, expect, it } from "vitest";
import { parsePlan } from "../src/lib/parse-plan";

describe("parsePlan", () => {
  it("returns empty for blank input", () => {
    expect(parsePlan("   \n")).toEqual([]);
  });

  it("splits checkbox jobs and keeps following detail lines", () => {
    const jobs = parsePlan(`
- [ ] Create Slack channel
  Use acfo-exact-sync
- [x] Invite Grok
- [ ] Launch Cursor on the cron fix
`);
    expect(jobs).toHaveLength(3);
    expect(jobs[0]).toEqual({
      title: "Create Slack channel",
      body: "Use acfo-exact-sync",
    });
    expect(jobs[1]?.title).toBe("Invite Grok");
    expect(jobs[2]?.title).toBe("Launch Cursor on the cron fix");
  });

  it("splits markdown headings", () => {
    const jobs = parsePlan(`
## Fix Railway cron
Keep tokens in Supabase.

## Seed WO-005
Add the Power Platform work order.
`);
    expect(jobs.map((job) => job.title)).toEqual(["Fix Railway cron", "Seed WO-005"]);
    expect(jobs[0]?.body).toContain("Keep tokens");
  });

  it("splits numbered lists when there are no checkboxes", () => {
    const jobs = parsePlan(`
1. Wire Slack OAuth
2. Invite grokbot
3. Hand over the plan
`);
    expect(jobs.map((job) => job.title)).toEqual([
      "Wire Slack OAuth",
      "Invite grokbot",
      "Hand over the plan",
    ]);
  });

  it("falls back to a single job for a blob of text", () => {
    const jobs = parsePlan("Just finish the Exact OAuth dance.");
    expect(jobs).toEqual([
      { title: "Just finish the Exact OAuth dance.", body: "" },
    ]);
  });
});
