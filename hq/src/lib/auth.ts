import { cookies } from "next/headers";
import type { Session } from "./types";

export const SESSION_COOKIE = "hq_session";

export function demoAllowed(): boolean {
  if (process.env.HQ_ALLOW_DEMO === "false") return false;
  return true;
}

export async function getSession(): Promise<Session | null> {
  const jar = await cookies();
  const raw = jar.get(SESSION_COOKIE)?.value;
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Session;
    if (!parsed.email || !parsed.name) return null;
    return parsed;
  } catch {
    return null;
  }
}

export async function setSession(session: Session): Promise<void> {
  const jar = await cookies();
  jar.set(SESSION_COOKIE, JSON.stringify(session), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
}

export async function clearSession(): Promise<void> {
  const jar = await cookies();
  jar.delete(SESSION_COOKIE);
}

export function appUrl(): string {
  return process.env.HQ_APP_URL || process.env.NEXT_PUBLIC_HQ_APP_URL || "http://localhost:3000";
}
