import { apiClient } from '@/lib/api';
import { TransactionForm } from '@/components/transaction-form';
import { TransactionList } from '@/components/transaction-list';
import { createTransaction } from './actions';
import type { Transaction, Category } from '@/types/api';

/**
 * Transactions page — shows the add-transaction form and the full transaction list.
 */
export default async function TransactionsPage() {
  const [transactions, categories] = await Promise.all([
    apiClient.get<Transaction[]>('/transactions'),
    apiClient.get<Category[]>('/categories'),
  ]);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-slate-800">Transactions</h1>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold text-slate-800">Add Transaction</h2>
        <TransactionForm categories={categories} action={createTransaction} />
      </div>

      <div>
        <h2 className="mb-4 text-xl font-semibold text-slate-800">All Transactions</h2>
        <TransactionList transactions={transactions} categories={categories} />
      </div>
    </div>
  );
}
