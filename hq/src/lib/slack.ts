export type SlackPostResult = {
  channel: string;
  ts: string;
  permalink?: string;
};

export type SlackClient = {
  createChannel(name: string): Promise<{ id: string; name: string }>;
  inviteUser(channelId: string, userId: string): Promise<void>;
  postMessage(input: {
    channel: string;
    text: string;
    threadTs?: string;
  }): Promise<SlackPostResult>;
  lookupUserByName(name: string): Promise<string | null>;
};

type SlackApiResponse = {
  ok: boolean;
  error?: string;
  channel?: { id: string; name: string };
  ts?: string;
  permalink?: string;
  members?: Array<{ id: string; name?: string; real_name?: string; is_bot?: boolean }>;
  response_metadata?: { next_cursor?: string };
};

async function slackCall(
  token: string,
  method: string,
  body: Record<string, unknown>,
): Promise<SlackApiResponse> {
  const response = await fetch(`https://slack.com/api/${method}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json; charset=utf-8",
    },
    body: JSON.stringify(body),
  });
  const json = (await response.json()) as SlackApiResponse;
  if (!json.ok) {
    throw new Error(json.error || `Slack ${method} failed`);
  }
  return json;
}

export function createSlackClient(token: string): SlackClient {
  return {
    async createChannel(name) {
      const normalized = name
        .toLowerCase()
        .replace(/[^a-z0-9-]/g, "-")
        .replace(/-+/g, "-")
        .slice(0, 80);
      const json = await slackCall(token, "conversations.create", {
        name: normalized,
        is_private: false,
      });
      if (!json.channel) throw new Error("Slack did not return a channel");
      return { id: json.channel.id, name: json.channel.name };
    },

    async inviteUser(channelId, userId) {
      await slackCall(token, "conversations.invite", {
        channel: channelId,
        users: userId,
      });
    },

    async postMessage(input) {
      const json = await slackCall(token, "chat.postMessage", {
        channel: input.channel,
        text: input.text,
        thread_ts: input.threadTs,
        unfurl_links: false,
      });
      if (!json.ts) throw new Error("Slack did not return a message ts");
      let permalink: string | undefined;
      try {
        const link = await slackCall(token, "chat.getPermalink", {
          channel: input.channel,
          message_ts: json.ts,
        });
        permalink = link.permalink;
      } catch {
        permalink = undefined;
      }
      return { channel: input.channel, ts: json.ts, permalink };
    },

    async lookupUserByName(name) {
      const target = name.toLowerCase();
      let cursor: string | undefined;
      do {
        const json = await slackCall(token, "users.list", {
          cursor,
          limit: 200,
        });
        const match = (json.members ?? []).find((member) => {
          const names = [member.name, member.real_name]
            .filter(Boolean)
            .map((value) => value!.toLowerCase());
          return names.some((value) => value === target || value.includes(target));
        });
        if (match) return match.id;
        cursor = json.response_metadata?.next_cursor || undefined;
      } while (cursor);
      return null;
    },
  };
}

export async function resolveGrokUserId(client: SlackClient): Promise<string | null> {
  if (process.env.SLACK_GROK_USER_ID) return process.env.SLACK_GROK_USER_ID;
  return client.lookupUserByName("grok");
}

export function slackOAuthUrl(state: string): string {
  const clientId = process.env.SLACK_CLIENT_ID;
  const redirect = process.env.SLACK_REDIRECT_URI;
  if (!clientId || !redirect) {
    throw new Error("SLACK_CLIENT_ID and SLACK_REDIRECT_URI are required");
  }
  const scopes = [
    "channels:manage",
    "channels:read",
    "chat:write",
    "users:read",
  ].join(",");
  const params = new URLSearchParams({
    client_id: clientId,
    scope: scopes,
    redirect_uri: redirect,
    state,
  });
  return `https://slack.com/oauth/v2/authorize?${params.toString()}`;
}

export async function exchangeSlackCode(code: string): Promise<{
  team_id: string;
  team_name: string;
  bot_token: string;
}> {
  const body = new URLSearchParams({
    client_id: process.env.SLACK_CLIENT_ID ?? "",
    client_secret: process.env.SLACK_CLIENT_SECRET ?? "",
    code,
    redirect_uri: process.env.SLACK_REDIRECT_URI ?? "",
  });
  const response = await fetch("https://slack.com/api/oauth.v2.access", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const json = (await response.json()) as {
    ok: boolean;
    error?: string;
    access_token?: string;
    team?: { id: string; name: string };
  };
  if (!json.ok || !json.access_token || !json.team) {
    throw new Error(json.error || "Slack OAuth failed");
  }
  return {
    team_id: json.team.id,
    team_name: json.team.name,
    bot_token: json.access_token,
  };
}
