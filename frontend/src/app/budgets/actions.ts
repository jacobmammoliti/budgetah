'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { apiClient, ApiError } from '@/lib/api';
import type { FormState, Budget, BudgetCopyResponse } from '@/types/api';

/**
 * Creates a new budget via the backend API.
 *
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: category_id, month, limit_amount.
 * @returns Updated form state with either a success flag or an error message.
 */
export async function createBudget(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    await apiClient.post<Budget>('/budgets', {
      category_id: Number(formData.get('category_id')),
      month: formData.get('month'),
      limit_amount: Number(formData.get('limit_amount')),
    });
    revalidatePath('/budgets');
    revalidatePath('/');
    return { success: true };
  } catch (err) {
    if (err instanceof ApiError) {
      return { success: false, error: err.detail };
    }
    throw err;
  }
}

/**
 * Updates the limit amount for an existing budget via the backend API.
 *
 * @param id - Budget ID to update.
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: limit_amount.
 * @returns Updated form state with either a success flag or an error message.
 */
export async function updateBudget(
  id: number,
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    await apiClient.put<Budget>(`/budgets/${id}`, {
      limit_amount: Number(formData.get('limit_amount')),
    });
    revalidatePath('/budgets');
    revalidatePath('/');
    return { success: true };
  } catch (err) {
    if (err instanceof ApiError) {
      return { success: false, error: err.detail };
    }
    throw err;
  }
}

/**
 * Deletes a budget via the backend API, then redirects to the budgets page.
 *
 * @param id - Budget ID to delete.
 */
export async function deleteBudget(id: number): Promise<void> {
  await apiClient.delete(`/budgets/${id}`);
  revalidatePath('/budgets');
  revalidatePath('/');
  redirect('/budgets');
}

/**
 * Copies all budgets from a source month to a target month.
 *
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: source_month, target_month.
 * @returns Updated form state with either a success message or an error.
 */
export async function copyBudgets(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    const result = await apiClient.post<BudgetCopyResponse>('/budgets/copy', {
      source_month: formData.get('source_month'),
      target_month: formData.get('target_month'),
    });
    revalidatePath('/budgets');
    revalidatePath('/');
    return {
      success: true,
      error: result.skipped_category_ids.length > 0
        ? `Copied ${result.copied} budget(s). Skipped ${result.skipped_category_ids.length} already-existing budget(s).`
        : undefined,
    };
  } catch (err) {
    if (err instanceof ApiError) {
      return { success: false, error: err.detail };
    }
    throw err;
  }
}
