import { apiClient } from '@/lib/api';
import { BudgetForm } from '@/components/budget-form';
import { BudgetList } from '@/components/budget-list';
import { CopyBudgetsForm } from '@/components/copy-budgets-form';
import { createBudget } from './actions';
import type { Budget, Category } from '@/types/api';

/**
 * Budgets page — shows the add-budget form, budget list, and copy-month utility.
 */
export default async function BudgetsPage() {
  const [budgets, categories] = await Promise.all([
    apiClient.get<Budget[]>('/budgets'),
    apiClient.get<Category[]>('/categories'),
  ]);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-slate-800">Budgets</h1>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold text-slate-800">Add Budget</h2>
        <BudgetForm categories={categories} action={createBudget} />
      </div>

      <div>
        <h2 className="mb-4 text-xl font-semibold text-slate-800">All Budgets</h2>
        <BudgetList budgets={budgets} categories={categories} />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold text-slate-800">Copy Budgets</h2>
        <p className="mb-4 text-sm text-slate-500">
          Copy all budget limits from one month to another.
        </p>
        <CopyBudgetsForm />
      </div>
    </div>
  );
}
