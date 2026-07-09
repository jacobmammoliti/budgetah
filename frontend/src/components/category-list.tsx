'use client';

import { useState } from 'react';
import { CategoryForm } from './category-form';
import { updateCategory, deleteCategory } from '@/app/categories/actions';
import type { Category } from '@/types/api';

/**
 * Renders a table of categories with inline edit and delete functionality.
 * Clicking "Edit" on a row swaps it for a pre-filled CategoryForm.
 *
 * @param categories - List of categories to display.
 */
export function CategoryList({ categories }: { categories: Category[] }) {
  const [editingId, setEditingId] = useState<number | null>(null);

  if (categories.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm">
        <p className="text-sm text-slate-500">No categories found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-left">
            <th className="px-4 py-3 font-medium text-slate-600">Name</th>
            <th className="px-4 py-3 font-medium text-slate-600">Description</th>
            <th className="px-4 py-3 font-medium text-slate-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((category) => (
            editingId === category.id ? (
              <tr key={category.id} className="border-b border-slate-100 last:border-0">
                <td colSpan={3} className="px-4 py-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">
                      Editing: {category.name}
                    </span>
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-xs text-slate-500 hover:text-slate-800"
                    >
                      Cancel
                    </button>
                  </div>
                  <CategoryForm
                    action={updateCategory.bind(null, category.id)}
                    category={category}
                    onSuccess={() => setEditingId(null)}
                  />
                </td>
              </tr>
            ) : (
              <tr
                key={category.id}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                <td className="px-4 py-3 font-medium text-slate-700">{category.name}</td>
                <td className="px-4 py-3 text-slate-600">
                  {category.description ?? <span className="italic text-slate-400">—</span>}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setEditingId(category.id)}
                      className="text-sm font-medium text-slate-600 hover:text-slate-900"
                    >
                      Edit
                    </button>
                    <form action={deleteCategory.bind(null, category.id)}>
                      <button
                        type="submit"
                        className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-500"
                      >
                        Delete
                      </button>
                    </form>
                  </div>
                </td>
              </tr>
            )
          ))}
        </tbody>
      </table>
    </div>
  );
}
