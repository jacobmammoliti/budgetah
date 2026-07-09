'use client';

import { useState, useActionState, useEffect } from 'react';
import { useFormStatus } from 'react-dom';
import { formatCurrency } from '@/lib/utils';
import { deleteBudget, updateBudget } from '@/app/budgets/actions';
import type { Budget, Category, FormState } from '@/types/api';

const INITIAL_STATE: FormState = { success: false };

function SaveButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="rounded-md bg-slate-800 px-3 py-1.5 text-sm text-white hover:bg-slate-700 disabled:opacity-50"
    >
      {pending ? 'Saving…' : 'Save'}
    </button>
  );
}

/**
 * Inline edit form for updating a budget's limit amount.
 *
 * @param budget - The budget being edited.
 * @param onCancel - Callback to close the edit form without saving.
 * @param onSaved - Callback invoked after a successful save.
 */
function EditAmountForm({
  budget,
  onCancel,
  onSaved,
}: {
  budget: Budget;
  onCancel: () => void;
  onSaved: () => void;
}) {
  const updateAction = updateBudget.bind(null, budget.id);
  const [state, formAction] = useActionState(updateAction, INITIAL_STATE);

  useEffect(() => {
    if (state.success) onSaved();
  }, [state.success, onSaved]);

  return (
    <form action={formAction} className="flex items-center gap-2">
      <input
        name="limit_amount"
        type="number"
        step="0.01"
        min="0.01"
        required
        defaultValue={budget.limit_amount}
        className="w-28 rounded-md border border-slate-300 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      />
      <SaveButton />
      <button
        type="button"
        onClick={onCancel}
        className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
      >
        Cancel
      </button>
      {!state.success && state.error && (
        <span className="text-xs text-red-600">{state.error}</span>
      )}
    </form>
  );
}

/**
 * Renders a table of budgets with edit and delete actions.
 *
 * @param budgets - List of budgets to display.
 * @param categories - List of categories used to resolve category names.
 */
export function BudgetList({
  budgets,
  categories,
}: {
  budgets: Budget[];
  categories: Category[];
}) {
  const categoryMap = new Map(categories.map((c) => [c.id, c.name]));
  const [editingId, setEditingId] = useState<number | null>(null);

  if (budgets.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm">
        <p className="text-sm text-slate-500">No budgets found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-left">
            <th className="px-4 py-3 font-medium text-slate-600">Category</th>
            <th className="px-4 py-3 font-medium text-slate-600">Month</th>
            <th className="px-4 py-3 text-right font-medium text-slate-600">Limit</th>
            <th className="px-4 py-3 font-medium text-slate-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          {budgets.map((budget) => {
            const deleteAction = deleteBudget.bind(null, budget.id);
            const isEditing = editingId === budget.id;

            return (
              <tr
                key={budget.id}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                <td className="px-4 py-3 font-medium text-slate-700">
                  {categoryMap.get(budget.category_id) ?? `Category ${budget.category_id}`}
                </td>
                <td className="px-4 py-3 text-slate-600">{budget.month}</td>
                <td className="px-4 py-3 text-right text-slate-700">
                  {formatCurrency(budget.limit_amount)}
                </td>
                <td className="px-4 py-3">
                  {isEditing ? (
                    <EditAmountForm
                      budget={budget}
                      onCancel={() => setEditingId(null)}
                      onSaved={() => setEditingId(null)}
                    />
                  ) : (
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setEditingId(budget.id)}
                        className="rounded-md bg-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-300"
                      >
                        Edit
                      </button>
                      <form action={deleteAction}>
                        <button
                          type="submit"
                          className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-500"
                        >
                          Delete
                        </button>
                      </form>
                    </div>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
