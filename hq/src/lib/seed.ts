import type { Project } from "./types";

export const SEEDED_PROJECTS: Omit<Project, "id" | "created_at">[] = [
  {
    name: "Exact sync → SQL → web",
    slug: "exact-sync",
    summary:
      "Exact Online → Railway cron → Supabase → web view. The main aCFO pipeline (PR #1).",
    github_pr_url: "https://github.com/Lennart1970/acfo/pull/1",
    default_ref: "cursor/exact-online-mysql-sync-4963",
    slack_channel_id: null,
    slack_channel_name: null,
    grok_invited: false,
  },
  {
    name: "Copilot Excel / dagoverzicht",
    slug: "excel-mvp",
    summary:
      "v1 daily booking skill: Excel dagoverzicht and Copilot scoring (PR #2).",
    github_pr_url: "https://github.com/Lennart1970/acfo/pull/2",
    default_ref: "cursor/copilot-excel-mvp-bc25",
    slack_channel_id: null,
    slack_channel_name: null,
    grok_invited: false,
  },
  {
    name: "Booking weekoverzicht v2",
    slug: "weekoverzicht",
    summary:
      "Weekly Excel upload → ISO week → Auto / AI / Human review routes (PR #3).",
    github_pr_url: "https://github.com/Lennart1970/acfo/pull/3",
    default_ref: "cursor/booking-weekoverzicht-v2-b1a5",
    slack_channel_id: null,
    slack_channel_name: null,
    grok_invited: false,
  },
  {
    name: "Cloud Agent env setup",
    slug: "env-setup",
    summary:
      "Cursor Cloud Agent environment: local Postgres, install/start scripts (PR #4).",
    github_pr_url: "https://github.com/Lennart1970/acfo/pull/4",
    default_ref: "cursor/dev-environment-setup-20b3",
    slack_channel_id: null,
    slack_channel_name: null,
    grok_invited: false,
  },
  {
    name: "MS admin work orders",
    slug: "ms-work-orders",
    summary:
      "Phase 2 queue for Microsoft admins: Copilot Studio, Entra, PostgREST, Power Platform (WO-001–005).",
    github_pr_url: "https://github.com/Lennart1970/acfo/pull/1",
    default_ref: "cursor/exact-online-mysql-sync-4963",
    slack_channel_id: null,
    slack_channel_name: null,
    grok_invited: false,
  },
];
