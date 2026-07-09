import { apiClient } from '@/lib/api';
import { TransactionForm } from '@/components/transaction-form';
import { updateTransaction, deleteTransaction } from '../actions';
import type { Transaction, Category } from '@/types/api';

/**
 * Transaction detail/edit page. Fetches the transaction and categories,
 * renders an edit form and a delete button.
 */
export default async function TransactionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const transactionId = Number(id);

  const [transaction, categories] = await Promise.all([
    apiClient.get<Transaction>(`/transactions/${transactionId}`),
    apiClient.get<Category[]>('/categories'),
  ]);

  const updateAction = updateTransaction.bind(null, transactionId);
  const deleteAction = deleteTransaction.bind(null, transactionId);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-slate-800">Edit Transaction</h1>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <TransactionForm
          categories={categories}
          transaction={transaction}
          action={updateAction}
        />
      </div>

      <div className="rounded-lg border border-red-100 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold text-slate-800">Danger Zone</h2>
        <p className="mb-4 text-sm text-slate-500">
          This action cannot be undone. The transaction will be permanently deleted.
        </p>
        <form action={deleteAction}>
          <button
            type="submit"
            className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-500"
          >
            Delete Transaction
          </button>
        </form>
      </div>
    </div>
  );
}
