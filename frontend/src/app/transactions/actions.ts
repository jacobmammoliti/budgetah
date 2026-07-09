'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { apiClient, ApiError } from '@/lib/api';
import type { FormState, Transaction } from '@/types/api';

/**
 * Creates a new transaction via the backend API.
 *
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: amount, type, description, date, category_id.
 * @returns Updated form state with either a success flag or an error message.
 */
export async function createTransaction(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    await apiClient.post<Transaction>('/transactions', {
      amount: Number(formData.get('amount')),
      type: formData.get('type'),
      description: formData.get('description') || null,
      date: formData.get('date'),
      category_id: formData.get('category_id') ? Number(formData.get('category_id')) : null,
    });
    revalidatePath('/transactions');
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
 * Updates an existing transaction via the backend API.
 *
 * @param id - Transaction ID to update.
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: amount, type, description, date, category_id.
 * @returns Updated form state with either a success flag or an error message.
 */
export async function updateTransaction(
  id: number,
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    await apiClient.put<Transaction>(`/transactions/${id}`, {
      amount: Number(formData.get('amount')),
      type: formData.get('type'),
      description: formData.get('description') || null,
      date: formData.get('date'),
      category_id: formData.get('category_id') ? Number(formData.get('category_id')) : null,
    });
    revalidatePath('/transactions');
    revalidatePath(`/transactions/${id}`);
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
 * Deletes a transaction via the backend API, then redirects to the transactions list.
 *
 * @param id - Transaction ID to delete.
 */
export async function deleteTransaction(id: number): Promise<void> {
  await apiClient.delete(`/transactions/${id}`);
  revalidatePath('/transactions');
  revalidatePath('/');
  redirect('/transactions');
}
