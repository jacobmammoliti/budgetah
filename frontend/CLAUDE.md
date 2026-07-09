# CLAUDE.md — Personal Budget Web App

## Project Overview

A minimal MVP web frontend for personal budgeting. Built with Next.js (App
Router), leaning entirely on React and Next.js built-ins — Server Components,
Server Actions, and the native `fetch` cache — instead of extra client-side
libraries. Consumes the Personal Budget API (FastAPI backend) to manage
**transactions** (income/expenses), **categories**, and **budget limits per
category**.

The guiding constraint for this project: keep the dependency list as small as
possible. Before adding any package, ask whether Next.js or React already
solves the problem natively.

---

## Tech Stack

| Concern          | Choice                                   | Version (latest stable) |
|-------------------|-------------------------------------------|--------------------------|
| Runtime           | Node.js                                   | 24.x (Active LTS)        |
| Language          | TypeScript                                | 6.0.x                    |
| Framework         | Next.js (App Router)                      | 16.2.x                   |
| UI library        | React                                     | 19.2.x                   |
| Styling           | Tailwind CSS (CSS-first config, v4)       | 4.3.x                    |
| Data fetching     | Native `fetch` in Server Components       | —                        |
| Mutations         | Next.js Server Actions                    | —                        |
| Forms             | Native `<form>` + React 19 `useActionState`/`useFormStatus` | — |
| Testing           | Vitest + React Testing Library            | latest stable            |
| Linting           | ESLint (`eslint-config-next`)             | bundled with Next.js     |
| Type checking     | `tsc --noEmit`                            | bundled with TypeScript  |
| Package manager   | npm (ships with Node, no extra install)   | bundled with Node.js     |

Deliberately **not** included, and why:

- **No React Query / SWR** — Next.js Server Components fetch and cache data
  natively; there's no client cache to manage for an MVP with no realtime
  needs.
- **No React Hook Form / Zod** — native HTML forms + Server Actions handle
  submission and pending state; validation errors come from the backend's
  `422` responses.
- **No component library (shadcn/ui, MUI, etc.)** — Tailwind utility classes
  on plain HTML elements are sufficient for the handful of forms/lists this
  MVP needs.
- **No Playwright / E2E suite** — deferred until the app has enough surface
  area to justify it (see Out of Scope).
- **No Prettier** — `eslint-config-next` covers linting; rely on the editor's
  formatter or add Prettier later if the team wants opinionated formatting.
- **No pnpm/yarn** — npm ships with Node.js, so there's one less tool to
  install and keep in sync.

Check for newer stable releases of each before starting new work — pin exact
versions in `package.json` and bump deliberately rather than floating on
`latest`.

---

## Project Structure

```
budget_web/
├── CLAUDE.md
├── README.md
├── package.json
├── tsconfig.json
├── next.config.ts
├── .eslintrc.json
├── vitest.config.ts
├── public/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── globals.css              # Tailwind v4 CSS-first config (@import "tailwindcss")
│   │   ├── page.tsx                 # Dashboard / overview
│   │   ├── error.tsx
│   │   ├── loading.tsx
│   │   ├── transactions/
│   │   │   ├── page.tsx
│   │   │   ├── actions.ts           # Server Actions: create/update/delete
│   │   │   └── [id]/page.tsx
│   │   ├── categories/
│   │   │   ├── page.tsx
│   │   │   └── actions.ts
│   │   └── budgets/
│   │       ├── page.tsx
│   │       └── actions.ts
│   ├── components/
│   │   ├── transaction-form.tsx
│   │   ├── transaction-list.tsx
│   │   ├── category-form.tsx
│   │   ├── category-list.tsx
│   │   ├── budget-form.tsx
│   │   └── budget-list.tsx
│   ├── lib/
│   │   ├── api.ts                   # Typed fetch wrapper for backend calls
│   │   └── utils.ts
│   └── types/
│       └── api.ts                   # Types mirroring backend schemas
└── tests/
    └── unit/
        ├── transactions.test.tsx
        ├── categories.test.tsx
        └── budgets.test.tsx
```

---

## Code Style

Adhere to the following standards in all code. When in doubt, favour clarity
over cleverness, and favour the platform (Next.js/React/browser) over a new
dependency.

### General Principles

- Explicit is better than implicit. Avoid hidden state, magic globals, or
  implicit side effects in components and Server Actions.
- Simple is better than complex. If a component needs a long explanation,
  split it into smaller components.
- Errors should never pass silently. Surface Server Action errors to the user
  via the returned form state; never swallow a `catch` block silently.
- Flat is better than nested. Prefer early returns and guard clauses over
  deeply nested JSX conditionals.
- Readability counts. Code is read far more often than it is written.
- Prefer a Next.js or React built-in over a third-party package. Only reach
  for a new dependency when the built-in genuinely can't do the job.

### TypeScript / React Conventions

- Strict mode enabled (`strict: true` in `tsconfig.json`); no `any` unless
  justified with a comment.
- Prefer named exports; default exports only for Next.js special files
  (`page.tsx`, `layout.tsx`, `error.tsx`, etc.).
- Use `PascalCase` for components, `camelCase` for functions/variables,
  `UPPER_SNAKE_CASE` for module-level constants.
- Server Components are the default; add `"use client"` only when a component
  needs interactivity, state, or browser APIs (e.g., a form using
  `useActionState`).
- Data fetching happens directly in `async` Server Components via
  `src/lib/api.ts`; mutations happen via Server Actions in each route's
  `actions.ts`.
- Co-locate component-specific types with the component; put shared/API types
  in `src/types/`.

### Formatting

- 2-space indentation.
- Single quotes for strings, double quotes only in JSX attributes.
- Semicolons required.
- Max line length: 100 characters.
- Imports ordered: React/Next → third-party → absolute (`@/...`) → relative,
  each group separated by a blank line.

### Documentation

- All exported functions, components, and Server Actions should have a short
  JSDoc comment describing purpose, params, and return value:
  ```tsx
  /**
   * Creates a new transaction via the backend API.
   *
   * @param _prevState - Previous form state (required by useActionState).
   * @param formData - Submitted form fields: amount, type, description, date, category_id.
   * @returns Updated form state with either a success flag or field errors.
   */
  export async function createTransaction(
    _prevState: TransactionFormState,
    formData: FormData,
  ): Promise<TransactionFormState> {
    // ...
  }
  ```

---

## Data Types

Types mirror the backend schemas exactly (`src/types/api.ts`).

### Category

```ts
interface Category {
  id: number;
  name: string;
  description: string | null;
  created_at: string; // ISO datetime
}
```

### Transaction

```ts
interface Transaction {
  id: number;
  amount: number;
  type: 'income' | 'expense';
  description: string | null;
  date: string; // ISO date (YYYY-MM-DD)
  category_id: number | null;
  created_at: string; // ISO datetime
}
```

### Budget

```ts
interface Budget {
  id: number;
  category_id: number;
  month: string; // ISO format YYYY-MM
  limit_amount: number;
  created_at: string; // ISO datetime
}
```

---

## Pages & Routes

| Route                | Description                                      |
|-----------------------|---------------------------------------------------|
| `/`                   | Dashboard — spending summary, budget progress      |
| `/transactions`       | List + filter transactions, create/edit forms      |
| `/transactions/[id]`  | Transaction detail / edit view                     |
| `/categories`         | Manage categories (CRUD)                           |
| `/budgets`            | Manage monthly budgets per category, copy-month action |

---

## API Integration

- The backend base URL is set via `NEXT_PUBLIC_API_BASE_URL` (defaults to
  `http://localhost:8000/api/v1` in development).
- All requests go through `src/lib/api.ts`, a thin typed wrapper around
  `fetch` that:
  - Prefixes the base URL.
  - Sets `Content-Type: application/json`.
  - Throws a typed `ApiError` (with `status` and `detail`) on non-2xx
    responses, parsed from the backend's `{"detail": "..."}` body.
- **Reads**: fetched directly inside `async` Server Components (e.g.,
  `app/transactions/page.tsx` calls `getTransactions()` at render time).
  Next.js's built-in `fetch` cache and request memoization handle
  de-duplication — no client-side cache library needed.
- **Writes**: performed via Server Actions colocated in each route's
  `actions.ts`. A Server Action calls the backend, then calls
  `revalidatePath()` for the affected route(s) so the next render picks up
  fresh data.

### Example Server Action Pattern

```ts
'use server';

import { revalidatePath } from 'next/cache';
import { apiClient, ApiError } from '@/lib/api';

export async function createTransaction(
  _prevState: TransactionFormState,
  formData: FormData,
): Promise<TransactionFormState> {
  try {
    await apiClient.post('/transactions', {
      amount: Number(formData.get('amount')),
      type: formData.get('type'),
      description: formData.get('description') || null,
      date: formData.get('date'),
      category_id: formData.get('category_id')
        ? Number(formData.get('category_id'))
        : null,
    });
    revalidatePath('/transactions');
    revalidatePath('/budgets');
    return { success: true };
  } catch (err) {
    if (err instanceof ApiError) {
      return { success: false, error: err.detail };
    }
    throw err;
  }
}
```

The corresponding client component uses React 19's `useActionState` and
`useFormStatus` for pending/error UI — no form library required.

---

## Error Handling

- Use `ApiError` (thrown by `lib/api.ts`) to distinguish expected API errors
  from unexpected runtime errors.
- Server Actions catch `ApiError` and return `{ success: false, error }` for
  the calling form to render inline; they let unexpected errors propagate so
  the nearest `error.tsx` boundary can handle them.
- Wrap each route segment in an `error.tsx` boundary for unexpected render
  errors.
- Use `loading.tsx` / Suspense boundaries for pending states on Server
  Component data fetches.

---

## State Management

- Server state (anything from the API) is not duplicated on the client — it's
  fetched fresh in Server Components and revalidated via `revalidatePath`
  after mutations.
- Local/UI-only state (modal open/closed, filter drafts before submit) uses
  component-local `useState` in client components.
- Pending/error state for mutations comes from `useActionState`, not a
  separate state library.
- No global client state library and no client-side data-fetching library —
  the App Router's server/cache model covers this MVP's needs.

---

## Testing

- Unit/component tests colocate under `tests/unit/`, one file per feature
  area (mirrors backend router-per-domain structure).
- Use Vitest + React Testing Library; query by role/label, not test IDs,
  where possible.
- Mock the API layer at the `lib/api.ts` boundary — do not mock individual
  `fetch` calls scattered across components.
- Every feature must have at minimum a happy-path test for its Server Action
  and its form component's client-side behavior (pending/error states).
- End-to-end testing (Playwright or similar) is deferred until the app has
  enough surface area to justify the added tooling — see Out of Scope.

Run tests with:

```bash
npm test
```

---

## Running Locally

```bash
# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Start the development server
npm run dev
```

The app will be available at `http://localhost:3000`.
Ensure the backend API is running at the URL configured in `.env.local`.

---

## Common Commands

```bash
# Lint and auto-fix
npm run lint -- --fix

# Type check
npm run typecheck

# Run unit tests
npm test

# Run unit tests with coverage
npm test -- --coverage

# Build for production
npm run build
```

---

## Out of Scope for MVP

The following are explicitly deferred — do not implement or add the
supporting dependency unless instructed:

- Authentication / user accounts / login screens
- Multi-currency support or currency formatting beyond a single locale
- Recurring transaction UI
- Charting/reporting dashboards beyond a basic budget-vs-actual summary
- Pagination or infinite scroll (render full result sets for now)
- Offline support / PWA features
- Internationalization (i18n)
- Client-side data-fetching library (TanStack Query/SWR) — revisit only if
  the app needs realtime updates, optimistic UI beyond what `useOptimistic`
  covers, or complex client-side cache invalidation.
- Form library (React Hook Form) and schema validation (Zod) — revisit only
  if forms grow complex enough that native validation + Server Action error
  returns become unwieldy.
- Component library (shadcn/ui, MUI, etc.) — revisit only if the number of
  distinct UI patterns grows enough to justify it.
- E2E test suite (Playwright) — revisit once core flows stabilize.
- Prettier / pnpm — revisit if the team standardizes on them.