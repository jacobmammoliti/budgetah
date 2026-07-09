'use client';

import { useActionState } from 'react';
import { useFormStatus } from 'react-dom';
import type { Category, FormState } from '@/types/api';

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
 * Form for creating or editing a category.
 *
 * @param action - Server Action to call on form submission.
 * @param category - Optional existing category (edit mode).
 * @param onSuccess - Optional callback invoked after a successful submission.
 */
export function CategoryForm({
  action,
  category,
  onSuccess,
}: {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  category?: Category;
  onSuccess?: () => void;
}) {
  const [state, formAction] = useActionState(
    async (prevState: FormState, formData: FormData) => {
      const result = await action(prevState, formData);
      if (result.success && onSuccess) {
        onSuccess();
      }
      return result;
    },
    INITIAL_STATE,
  );

  return (
    <form action={formAction} className="space-y-4">
      {state.success && (
        <p className="text-sm text-green-600">Category saved successfully.</p>
      )}
      {!state.success && state.error && (
        <p className="text-sm text-red-600">{state.error}</p>
      )}

      <div>
        <label htmlFor="name" className="mb-1 block text-sm font-medium text-slate-700">
          Name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          defaultValue={category?.name ?? ''}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
        />
      </div>

      <div>
        <label htmlFor="description" className="mb-1 block text-sm font-medium text-slate-700">
          Description
        </label>
        <input
          id="description"
          name="description"
          type="text"
          defaultValue={category?.description ?? ''}
          placeholder="Optional"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
        />
      </div>

      <SubmitButton label={category ? 'Update Category' : 'Add Category'} />
    </form>
  );
}
