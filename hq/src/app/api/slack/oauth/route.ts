import { NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { slackOAuthUrl } from "@/lib/slack";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.redirect(new URL("/login", process.env.HQ_APP_URL || "http://localhost:3000"));
  }
  try {
    const state = crypto.randomUUID();
    const response = NextResponse.redirect(slackOAuthUrl(state));
    response.cookies.set("hq_slack_oauth_state", state, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      maxAge: 600,
    });
    return response;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Slack is not configured";
    return NextResponse.redirect(
      new URL(`/?error=${encodeURIComponent(message)}`, process.env.HQ_APP_URL || "http://localhost:3000"),
    );
  }
}
