/**
 * Shared utility functions for formatting and date helpers.
 */

/**
 * Formats a number as USD currency string.
 *
 * @param amount - The numeric amount to format
 * @returns Formatted currency string (e.g. '$1,234.56')
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

/**
 * Formats a date string into a human-readable format.
 * Handles YYYY-MM-DD strings without timezone shift by parsing date parts directly.
 *
 * @param dateStr - ISO date string (YYYY-MM-DD or ISO datetime)
 * @returns Formatted date string (e.g. 'Jan 15, 2025')
 */
export function formatDate(dateStr: string): string {
  // For YYYY-MM-DD strings, parse parts directly to avoid UTC→local timezone shift
  const datePart = dateStr.slice(0, 10);
  const [year, month, day] = datePart.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Returns the current month in YYYY-MM format.
 *
 * @returns Current month string (e.g. '2025-01')
 */
export function currentMonth(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

/**
 * Returns the first and last day of a given YYYY-MM month as ISO date strings.
 *
 * @param month - Month string in YYYY-MM format
 * @returns Object with startDate and endDate as YYYY-MM-DD strings
 */
export function monthBounds(month: string): { startDate: string; endDate: string } {
  const [year, mon] = month.split('-').map(Number);
  const startDate = `${month}-01`;
  const lastDay = new Date(year, mon, 0).getDate();
  const endDate = `${month}-${String(lastDay).padStart(2, '0')}`;
  return { startDate, endDate };
}
