import { NextResponse } from "next/server";
import { usesSupabase } from "@/lib/store";

export async function GET() {
  return NextResponse.json({
    ok: true,
    store: usesSupabase() ? "supabase" : "file",
  });
}
