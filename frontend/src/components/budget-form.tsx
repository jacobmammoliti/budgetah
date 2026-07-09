'use client';

import { useActionState } from 'react';
import { useFormStatus } from 'react-dom';
import { currentMonth } from '@/lib/utils';
import type { Category, Budget, FormState } from '@/types/api';

const INITIAL_STATE: FormState = { success: false };

/** Submit button that disables itself and shows a loading label while the form is pending. */
function SubmitButton({ label }: { label: string }) {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="rounded-md bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700 disabled:opacity-50"
    >
      {pending ? 'Saving…' : label}
    </button>
  );
}

/**
 * Form for creating or editing a monthly budget limit.
 *
 * @param categories - List of categories to populate the category selector.
 * @param action - Server Action to call on form submission.
 * @param budget - Optional existing budget (edit mode).
 */
export function BudgetForm({
  categories,
  action,
  budget,
}: {
  categories: Category[];
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  budget?: Budget;
}) {
  const [state, formAction] = useActionState(action, INITIAL_STATE);

  return (
    <form action={formAction} className="space-y-4">
      {state.success && (
        <p className="text-sm text-green-600">Budget saved successfully.</p>
      )}
      {!state.success && state.error && (
        <p className="text-sm text-red-600">{state.error}</p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label htmlFor="category_id" className="mb-1 block text-sm font-medium text-slate-700">
            Category
          </label>
          <select
            id="category_id"
            name="category_id"
            required
            defaultValue={budget?.category_id ?? ''}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            <option value="" disabled>
              Select a category
            </option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="month" className="mb-1 block text-sm font-medium text-slate-700">
            Month
          </label>
          <input
            id="month"
            name="month"
            type="month"
            required
            defaultValue={budget?.month ?? currentMonth()}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
        </div>

        <div>
          <label htmlFor="limit_amount" className="mb-1 block text-sm font-medium text-slate-700">
            Limit Amount
          </label>
          <input
            id="limit_amount"
            name="limit_amount"
            type="number"
            step="0.01"
            min="0"
            required
            defaultValue={budget?.limit_amount}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
        </div>
      </div>

      <SubmitButton label={budget ? 'Update Budget' : 'Add Budget'} />
    </form>
  );
}
