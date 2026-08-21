'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { apiClient, ApiError } from '@/lib/api';
import type { FormState, Category } from '@/types/api';

/**
 * Creates a new category via the backend API.
 *
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: name, description.
 * @returns Updated form state with either a success flag or an error message.
 */
export async function createCategory(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    await apiClient.post<Category>('/categories', {
      name: formData.get('name'),
      description: formData.get('description') || null,
    });
    revalidatePath('/categories');
    return { success: true };
  } catch (err) {
    if (err instanceof ApiError) {
      return { success: false, error: err.detail };
    }
    throw err;
  }
}

/**
 * Updates an existing category via the backend API.
 *
 * @param id - Category ID to update.
 * @param _prevState - Previous form state (required by useActionState).
 * @param formData - Submitted form fields: name, description.
 * @returns Updated form state with either a success flag or an error message.
 */
export async function updateCategory(
  id: number,
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  try {
    await apiClient.put<Category>(`/categories/${id}`, {
      name: formData.get('name'),
      description: formData.get('description') || null,
    });
    revalidatePath('/categories');
    return { success: true };
  } catch (err) {
    if (err instanceof ApiError) {
      return { success: false, error: err.detail };
    }
    throw err;
  }
}

/**
 * Deletes a category via the backend API, then redirects to the categories page.
 *
 * @param id - Category ID to delete.
 */
export async function deleteCategory(id: number): Promise<void> {
  await apiClient.delete(`/categories/${id}`);
  revalidatePath('/categories');
  redirect('/categories');
}
