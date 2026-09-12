import { redirect } from "next/navigation";
import { Shell } from "@/components/Shell";
import { getSession } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function HqLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession();
  if (!session) redirect("/login");
  return <Shell session={session}>{children}</Shell>;
}
