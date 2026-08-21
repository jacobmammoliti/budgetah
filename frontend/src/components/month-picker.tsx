'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';

interface MonthPickerProps {
  month: string; // YYYY-MM
}

function offsetMonth(month: string, delta: number): string {
  const [year, mon] = month.split('-').map(Number);
  const d = new Date(year, mon - 1 + delta, 1);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

/**
 * Prev/next month navigation links for the dashboard.
 * Updates the `?month=YYYY-MM` search param in the URL.
 *
 * @param month - Currently displayed month in YYYY-MM format.
 */
export function MonthPicker({ month }: MonthPickerProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function hrefFor(m: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set('month', m);
    return `${pathname}?${params.toString()}`;
  }

  const [year, mon] = month.split('-').map(Number);
  const label = new Date(year, mon - 1, 1).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className="flex items-center gap-3">
      <Link
        href={hrefFor(offsetMonth(month, -1))}
        className="rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-600 hover:bg-slate-50"
        aria-label="Previous month"
      >
        ‹
      </Link>
      <span className="min-w-32 text-center text-2xl font-bold text-slate-800">{label}</span>
      <Link
        href={hrefFor(offsetMonth(month, +1))}
        className="rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-600 hover:bg-slate-50"
        aria-label="Next month"
      >
        ›
      </Link>
    </div>
  );
}
