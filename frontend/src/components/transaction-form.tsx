'use client';

import { useActionState } from 'react';
import { useFormStatus } from 'react-dom';
import type { Category, Transaction, FormState } from '@/types/api';

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
      {pending ? 'Saving…' : 'Save Transaction'}
    </button>
  );
}

/**
 * Form for creating or editing a transaction.
 *
 * @param categories - List of categories to populate the category selector.
 * @param transaction - Optional existing transaction (edit mode).
 * @param action - Server Action to call on form submission.
 */
export function TransactionForm({
  categories,
  transaction,
  action,
}: {
  categories: Category[];
  transaction?: Transaction;
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
}) {
  const [state, formAction] = useActionState(action, INITIAL_STATE);

  const today = new Date().toISOString().slice(0, 10);

  return (
    <form action={formAction} className="space-y-4">
      {state.success && (
        <p className="text-sm text-green-600">Transaction saved successfully.</p>
      )}
      {!state.success && state.error && (
        <p className="text-sm text-red-600">{state.error}</p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="amount" className="mb-1 block text-sm font-medium text-slate-700">
            Amount
          </label>
          <input
            id="amount"
            name="amount"
            type="number"
            step="0.01"
            min="0"
            required
            defaultValue={transaction?.amount}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
        </div>

        <div>
          <label htmlFor="type" className="mb-1 block text-sm font-medium text-slate-700">
            Type
          </label>
          <select
            id="type"
            name="type"
            required
            defaultValue={transaction?.type ?? 'expense'}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
            <option value="savings">Savings</option>
          </select>
        </div>

        <div>
          <label htmlFor="date" className="mb-1 block text-sm font-medium text-slate-700">
            Date
          </label>
          <input
            id="date"
            name="date"
            type="date"
            required
            defaultValue={transaction?.date ?? today}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
        </div>

        <div>
          <label htmlFor="category_id" className="mb-1 block text-sm font-medium text-slate-700">
            Category
          </label>
          <select
            id="category_id"
            name="category_id"
            defaultValue={transaction?.category_id ?? ''}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            <option value="">— None —</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="description" className="mb-1 block text-sm font-medium text-slate-700">
          Description
        </label>
        <input
          id="description"
          name="description"
          type="text"
          defaultValue={transaction?.description ?? ''}
          placeholder="Optional"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
        />
      </div>

      <SubmitButton />
    </form>
  );
}
