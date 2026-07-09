/**
 * Global loading skeleton shown while Server Component data is being fetched.
 */
export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 animate-pulse rounded-md bg-slate-200" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-lg border border-slate-200 bg-slate-100"
          />
        ))}
      </div>
      <div className="h-64 animate-pulse rounded-lg border border-slate-200 bg-slate-100" />
    </div>
  );
}
