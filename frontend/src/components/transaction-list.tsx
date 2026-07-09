import Link from 'next/link';
import { formatCurrency, formatDate } from '@/lib/utils';
import type { Transaction, Category } from '@/types/api';

/**
 * Renders a table of transactions with links to their detail/edit pages.
 *
 * @param transactions - List of transactions to display.
 * @param categories - List of categories used to resolve category names.
 */
export function TransactionList({
  transactions,
  categories,
}: {
  transactions: Transaction[];
  categories: Category[];
}) {
  const categoryMap = new Map(categories.map((c) => [c.id, c.name]));

  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm">
        <p className="text-sm text-slate-500">No transactions found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-left">
            <th className="px-4 py-3 font-medium text-slate-600">Date</th>
            <th className="px-4 py-3 font-medium text-slate-600">Type</th>
            <th className="px-4 py-3 font-medium text-slate-600">Description</th>
            <th className="px-4 py-3 font-medium text-slate-600">Category</th>
            <th className="px-4 py-3 text-right font-medium text-slate-600">Amount</th>
            <th className="px-4 py-3 font-medium text-slate-600"></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr
              key={t.id}
              className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
            >
              <td className="px-4 py-3 text-slate-600">{formatDate(t.date)}</td>
              <td className="px-4 py-3">
                <span
                  className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                    t.type === 'income'
                      ? 'bg-green-100 text-green-700'
                      : t.type === 'savings'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-red-100 text-red-700'
                  }`}
                >
                  {t.type}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-700">
                {t.description ?? <span className="italic text-slate-400">—</span>}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {t.category_id ? (categoryMap.get(t.category_id) ?? '—') : '—'}
              </td>
              <td
                className={`px-4 py-3 text-right font-medium ${
                  t.type === 'income'
                    ? 'text-green-600'
                    : t.type === 'savings'
                      ? 'text-blue-600'
                      : 'text-red-600'
                }`}
              >
                {formatCurrency(t.amount)}
              </td>
              <td className="px-4 py-3">
                <Link
                  href={`/transactions/${t.id}`}
                  className="text-xs font-medium text-slate-500 hover:text-slate-800 hover:underline"
                >
                  Edit
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
