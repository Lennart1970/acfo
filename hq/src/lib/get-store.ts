import "server-only";

import { createFileStore } from "./file-store";
import { usesSupabase } from "./store";
import { createSupabaseStore } from "./supabase-store";
import type { Store } from "./store";

let cached: Store | null = null;

export function getStore(): Store {
  if (cached) return cached;
  cached = usesSupabase() ? createSupabaseStore() : createFileStore();
  return cached;
}
