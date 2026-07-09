/**
 * Shared TypeScript interfaces mirroring backend API schemas exactly.
 */

/** A spending/expense category for grouping transactions. */
export interface Category {
  id: number;
  name: string;
  description: string | null;
  created_at: string; // ISO datetime
}

/** A single financial transaction (income or expense). */
export interface Transaction {
  id: number;
  amount: number;
  type: 'income' | 'expense' | 'savings';
  description: string | null;
  date: string; // ISO date YYYY-MM-DD
  category_id: number | null;
  created_at: string; // ISO datetime
}

/** A monthly budget limit for a specific category. */
export interface Budget {
  id: number;
  category_id: number;
  month: string; // YYYY-MM
  limit_amount: number;
  created_at: string; // ISO datetime
}

/** Per-category spending breakdown within a time period. */
export interface SpendingCategoryBreakdown {
  category: string;
  total: number;
}

/** Aggregated spending response from the backend spending endpoint. */
export interface SpendingResponse {
  period_start: string;
  period_end: string;
  total: number;
  breakdown: SpendingCategoryBreakdown[];
}

/** Response from the budget copy endpoint. */
export interface BudgetCopyResponse {
  copied: number;
  skipped_category_ids: number[];
}

/** Shared form state type used by all Server Actions with useActionState. */
export type FormState = { success: boolean; error?: string };
