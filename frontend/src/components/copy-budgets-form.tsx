'use client';

import { useActionState } from 'react';
import { useFormStatus } from 'react-dom';
import { currentMonth } from '@/lib/utils';
import { copyBudgets } from '@/app/budgets/actions';
import type { FormState } from '@/types/api';

const INITIAL_STATE: FormState = { success: false };

/** Submit button that disables itself and shows a loading label while the form is pending. */
function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="rounded-md bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700 disabled:opacity-50"
    >
      {pending ? 'Copying…' : 'Copy Budgets'}
    </button>
  );
}

/**
 * Small client component for copying budgets from one month to another.
 * Renders source/target month inputs and calls the copyBudgets Server Action.
 */
export function CopyBudgetsForm() {
  const [state, formAction] = useActionState(copyBudgets, INITIAL_STATE);
  const month = currentMonth();

  return (
    <form action={formAction} className="space-y-4">
      {state.success && (
        <p className="text-sm text-green-600">
          {state.error ?? 'Budgets copied successfully.'}
        </p>
      )}
      {!state.success && state.error && (
        <p className="text-sm text-red-600">{state.error}</p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label
            htmlFor="source_month"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Source Month
          </label>
          <input
            id="source_month"
            name="source_month"
            type="month"
            required
            defaultValue={month}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
        </div>

        <div>
          <label
            htmlFor="target_month"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Target Month
          </label>
          <input
            id="target_month"
            name="target_month"
            type="month"
            required
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
        </div>
      </div>

      <SubmitButton />
    </form>
  );
}
