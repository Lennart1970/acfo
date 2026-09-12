export function Flash({
  notice,
  error,
}: {
  notice?: string;
  error?: string;
}) {
  if (!notice && !error) return null;
  return (
    <div className="mb-6 space-y-2">
      {notice ? (
        <p className="rounded-lg border border-green/30 bg-green/10 px-4 py-3 text-sm text-green-dark">
          {notice}
        </p>
      ) : null}
      {error ? (
        <p className="rounded-lg border border-rose/30 bg-rose/10 px-4 py-3 text-sm text-rose">
          {error}
        </p>
      ) : null}
    </div>
  );
}
