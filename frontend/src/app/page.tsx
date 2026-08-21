import { Suspense } from 'react';

import { apiClient } from '@/lib/api';
import { formatCurrency, currentMonth, monthBounds } from '@/lib/utils';
import { MonthPicker } from '@/components/month-picker';
import type { Transaction, Budget, Category } from '@/types/api';

/**
 * Dashboard page — shows the selected month's income/expense summary
 * and budget progress. Month is controlled via the `?month=YYYY-MM` param.
 *
 * @param searchParams - Next.js dynamic search params (awaited).
 */
export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ month?: string }>;
}) {
  const { month: rawMonth } = await searchParams;
  const month = rawMonth && /^\d{4}-\d{2}$/.test(rawMonth) ? rawMonth : currentMonth();
  const { startDate, endDate } = monthBounds(month);

  const [transactions, budgets, categories] = await Promise.all([
    apiClient.get<Transaction[]>(`/transactions?start_date=${startDate}&end_date=${endDate}`),
    apiClient.get<Budget[]>('/budgets'),
    apiClient.get<Category[]>('/categories'),
  ]);

  const categoryMap = new Map(categories.map((c) => [c.id, c.name]));

  const income = transactions
    .filter((t) => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0);

  const expenses = transactions
    .filter((t) => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0);

  const savings = transactions
    .filter((t) => t.type === 'savings')
    .reduce((sum, t) => sum + t.amount, 0);

  const net = income - expenses;

  const monthBudgets = budgets.filter((b) => b.month === month);

  const spendingByCategory = new Map<number, number>();
  for (const t of transactions) {
    if ((t.type === 'expense' || t.type === 'savings') && t.category_id !== null) {
      spendingByCategory.set(
        t.category_id,
        (spendingByCategory.get(t.category_id) ?? 0) + t.amount,
      );
    }
  }

  return (
    <div className="space-y-8">
      <Suspense>
        <MonthPicker month={month} />
      </Suspense>

      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Income</p>
          <p className="mt-1 text-2xl font-semibold text-green-600">{formatCurrency(income)}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Expenses</p>
          <p className="mt-1 text-2xl font-semibold text-red-600">{formatCurrency(expenses)}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Savings</p>
          <p className="mt-1 text-2xl font-semibold text-blue-600">{formatCurrency(savings)}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Net Balance</p>
          <p className={`mt-1 text-2xl font-semibold ${net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(net)}
          </p>
        </div>
      </div>

      {/* Budget progress */}
      <div>
        <h2 className="text-xl font-semibold text-slate-800">Budget Progress</h2>
        {monthBudgets.length === 0 ? (
          <div className="mt-4 rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm">
            <p className="text-sm text-slate-500">No budgets set for this month.</p>
          </div>
        ) : (
          <div className="mt-4 space-y-3">
            {monthBudgets.map((budget) => {
              const spent = spendingByCategory.get(budget.category_id) ?? 0;
              const pct =
                budget.limit_amount > 0
                  ? Math.min((spent / budget.limit_amount) * 100, 100)
                  : 0;
              const overBudget = spent > budget.limit_amount;
              const categoryName =
                categoryMap.get(budget.category_id) ?? `Category ${budget.category_id}`;

              return (
                <div
                  key={budget.id}
                  className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">{categoryName}</span>
                    <span className="text-sm text-slate-500">
                      {formatCurrency(spent)} / {formatCurrency(budget.limit_amount)}
                    </span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-100">
                    <div
                      className={`h-2 rounded-full ${overBudget ? 'bg-red-500' : 'bg-green-500'}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  {overBudget && (
                    <p className="mt-1 text-xs text-red-600">
                      Over budget by {formatCurrency(spent - budget.limit_amount)}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
