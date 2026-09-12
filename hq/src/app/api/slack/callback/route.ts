import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { appUrl, getSession } from "@/lib/auth";
import { getStore } from "@/lib/get-store";
import { exchangeSlackCode } from "@/lib/slack";

export async function GET(request: Request) {
  const session = await getSession();
  const base = appUrl();
  if (!session) {
    return NextResponse.redirect(new URL("/login", base));
  }

  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const jar = await cookies();
  const expected = jar.get("hq_slack_oauth_state")?.value;

  if (!code || !state || !expected || state !== expected) {
    return NextResponse.redirect(new URL("/?error=Slack%20OAuth%20state%20mismatch", base));
  }

  try {
    const installation = await exchangeSlackCode(code);
    await getStore().upsertSlackInstallation(installation);
    const response = NextResponse.redirect(new URL("/?notice=Slack%20connected", base));
    response.cookies.delete("hq_slack_oauth_state");
    return response;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Slack OAuth failed";
    return NextResponse.redirect(new URL(`/?error=${encodeURIComponent(message)}`, base));
  }
}
