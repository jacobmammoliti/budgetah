import { apiClient } from '@/lib/api';
import { CategoryForm } from '@/components/category-form';
import { CategoryList } from '@/components/category-list';
import { createCategory } from './actions';
import type { Category } from '@/types/api';

/**
 * Categories page — shows the add-category form and the full category list.
 */
export default async function CategoriesPage() {
  const categories = await apiClient.get<Category[]>('/categories');

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-slate-800">Categories</h1>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold text-slate-800">Add Category</h2>
        <CategoryForm action={createCategory} />
      </div>

      <div>
        <h2 className="mb-4 text-xl font-semibold text-slate-800">All Categories</h2>
        <CategoryList categories={categories} />
      </div>
    </div>
  );
}
