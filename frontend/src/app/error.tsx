'use client';

/**
 * Global error boundary for unexpected render errors.
 * Displays the error message and a reset button to retry rendering.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4 text-center">
      <h2 className="text-xl font-semibold text-slate-800">Something went wrong</h2>
      <p className="max-w-md text-sm text-slate-600">
        {error.message ?? 'An unexpected error occurred. Please try again.'}
      </p>
      <button
        onClick={reset}
        className="rounded-md bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700 disabled:opacity-50"
      >
        Try again
      </button>
    </div>
  );
}
