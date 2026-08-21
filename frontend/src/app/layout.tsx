import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'Budgetah',
  description: 'Personal budget tracker',
};

/**
 * Root layout with top navigation bar and main content area.
 * Wraps all pages with consistent chrome.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-slate-50">
        <nav className="border-b border-slate-200 bg-white shadow-sm">
          <div className="mx-auto flex max-w-4xl items-center gap-6 px-4 py-3">
            <Link href="/" className="text-lg font-bold text-slate-800 hover:text-slate-600">
              Budgetah
            </Link>
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="text-sm font-medium text-slate-600 hover:text-slate-900"
              >
                Dashboard
              </Link>
              <Link
                href="/transactions"
                className="text-sm font-medium text-slate-600 hover:text-slate-900"
              >
                Transactions
              </Link>
              <Link
                href="/categories"
                className="text-sm font-medium text-slate-600 hover:text-slate-900"
              >
                Categories
              </Link>
              <Link
                href="/budgets"
                className="text-sm font-medium text-slate-600 hover:text-slate-900"
              >
                Budgets
              </Link>
            </div>
          </div>
        </nav>
        <main className="flex-1 px-4 py-8">
          <div className="mx-auto max-w-4xl">{children}</div>
        </main>
      </body>
    </html>
  );
}
