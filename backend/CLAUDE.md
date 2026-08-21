# CLAUDE.md — Personal Budget API

## Project Overview

A minimal MVP REST API for personal budgeting. Built with FastAPI and SQLite.
Covers three core domains: **transactions** (income/expenses), **categories**, and
**budget limits per category**.

---

## Tech Stack

| Concern        | Choice                          |
|----------------|---------------------------------|
| Language       | Python 3.14                     |
| Framework      | FastAPI (latest)                |
| Database       | SQLite via `aiosqlite` (async)  |
| ORM            | SQLAlchemy 2.x (async core)     |
| Validation     | Pydantic v2 (bundled with FastAPI) |
| Migrations     | Alembic                         |
| Testing        | pytest + httpx (async client)   |
| Linting        | Ruff                            |
| Type checking  | mypy (strict)                   |

---

## Project Structure

```
budget_api/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app factory and lifespan
│   ├── database.py        # Async engine, session factory
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── categories.py
│   │   ├── transactions.py
│   │   └── budgets.py
│   └── crud/
│       ├── __init__.py
│       ├── categories.py
│       ├── transactions.py
│       └── budgets.py
└── tests/
    ├── conftest.py
    ├── test_categories.py
    ├── test_transactions.py
    └── test_budgets.py
```

---

## Code Style

Adhere to the following standards in all code. When in doubt, favour clarity
over cleverness — this is the Zen of Python.

### PEP 20 — The Zen of Python

- Explicit is better than implicit. Never rely on side effects or hidden state.
- Simple is better than complex. If a function needs a long explanation, split it.
- Errors should never pass silently. Raise `HTTPException` with a meaningful
  `detail` string; never swallow exceptions with a bare `except`.
- Flat is better than nested. Prefer early returns over deeply nested conditionals.
- Readability counts. Code is read far more often than it is written.

### PEP 8 — Style Guide

- 4-space indentation, no tabs.
- Maximum line length: **88 characters** (Ruff default; aligns with Black).
- Two blank lines between top-level definitions; one blank line between methods.
- Imports ordered: standard library → third-party → local, each group separated
  by a blank line.
- Use `snake_case` for functions, variables, and modules; `PascalCase` for
  classes; `UPPER_SNAKE_CASE` for module-level constants.
- Avoid wildcard imports (`from module import *`).

### Google Python Style Guide (additions/overrides)

- All public functions, classes, and methods **must** have docstrings using the
  Google docstring format:
  ```python
  def create_category(name: str, description: str | None = None) -> Category:
      """Creates a new budget category.

      Args:
          name: Human-readable category label (e.g., "Groceries").
          description: Optional longer description of the category.

      Returns:
          The newly created Category ORM instance.

      Raises:
          ValueError: If `name` is an empty string.
      """
  ```
- Use type annotations on every function signature — parameters and return type.
- Prefer `|` union syntax over `Optional[X]` (Python 3.10+).
- Avoid mutable default arguments. Use `None` as the default and assign inside
  the function body.
- Module-level `__all__` is optional for internal packages but required for any
  public-facing module.

---

## Data Models

### Category

Represents a named grouping for transactions (e.g., "Groceries", "Rent").

| Column        | Type         | Notes                         |
|---------------|--------------|-------------------------------|
| `id`          | INTEGER PK   | Auto-increment                |
| `name`        | TEXT         | Unique, not null              |
| `description` | TEXT         | Nullable                      |
| `created_at`  | DATETIME     | Server default: `now()`       |

### Transaction

A single income or expense event.

| Column          | Type       | Notes                                    |
|-----------------|------------|------------------------------------------|
| `id`            | INTEGER PK | Auto-increment                           |
| `amount`        | REAL       | Positive value; sign inferred from type  |
| `type`          | TEXT       | `"income"` or `"expense"`               |
| `description`   | TEXT       | Nullable                                 |
| `date`          | DATE       | Defaults to today                        |
| `category_id`   | INTEGER FK | References `categories.id`, nullable     |
| `created_at`    | DATETIME   | Server default: `now()`                  |

### Budget

A spending limit for a category in a given month.

| Column        | Type         | Notes                             |
|---------------|--------------|-----------------------------------|
| `id`          | INTEGER PK   | Auto-increment                    |
| `category_id` | INTEGER FK   | References `categories.id`        |
| `month`       | TEXT         | ISO format: `"YYYY-MM"`           |
| `limit_amount`| REAL         | Must be > 0                       |
| `created_at`  | DATETIME     | Server default: `now()`           |

Unique constraint on `(category_id, month)` — one budget per category per month.

---

## API Endpoints

All routes are prefixed with `/api/v1`.

### Categories

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/categories`           | List all categories      |
| POST   | `/categories`           | Create a category        |
| GET    | `/categories/{id}`      | Get a single category    |
| PUT    | `/categories/{id}`      | Update a category        |
| DELETE | `/categories/{id}`      | Delete a category        |

### Transactions

| Method | Path                      | Description                          |
|--------|---------------------------|--------------------------------------|
| GET    | `/transactions`           | List transactions (filterable)       |
| POST   | `/transactions`           | Record a transaction                 |
| GET    | `/transactions/{id}`      | Get a single transaction             |
| PUT    | `/transactions/{id}`      | Update a transaction                 |
| DELETE | `/transactions/{id}`      | Delete a transaction                 |

Supported query parameters for `GET /transactions`:
- `type` — `"income"` or `"expense"`
- `category_id` — filter by category
- `start_date` / `end_date` — ISO date strings (`YYYY-MM-DD`)

### Budgets

| Method | Path                          | Description                              |
|--------|-------------------------------|------------------------------------------|
| GET    | `/budgets`                    | List all budgets                         |
| POST   | `/budgets`                    | Create or update a budget                |
| GET    | `/budgets/{id}`               | Get a single budget                      |
| DELETE | `/budgets/{id}`               | Delete a budget                          |
| POST   | `/budgets/copy`               | Copy all budgets from one month to another |

#### `POST /budgets/copy`

Request body:

```json
{
  "source_month": "2025-06",
  "target_month": "2025-07"
}
```

Behaviour:
- Copies all budget rows where `month == source_month` into new rows with `month == target_month`.
- If a budget for a given category already exists in `target_month`, it is **skipped** (not overwritten). Return a list of skipped `category_id`s in the response so the caller knows.
- If `source_month` has no budgets, return `404`.
- `source_month` and `target_month` must be different; return `422` if they are equal.

Response body:

```json
{
  "copied": 4,
  "skipped_category_ids": [3]
}
```

---

## Error Handling

- Use `HTTPException` from FastAPI for all expected error conditions.
- Standard HTTP status codes only — do not invent new ones.
- Return a consistent error body; FastAPI's default `{"detail": "..."}` is
  sufficient for the MVP.
- Common patterns:
  - `404` — resource not found (use a shared `_get_or_404` helper in each CRUD module)
  - `409` — unique constraint violation (e.g., duplicate budget for same month)
  - `422` — invalid input (handled automatically by Pydantic)
  - `500` — unexpected server errors (log and let FastAPI's default handler respond)

---

## Database & Sessions

- Use SQLAlchemy 2.x async engine backed by `aiosqlite`.
- Session lifecycle is managed via FastAPI dependency injection:
  ```python
  async def get_session() -> AsyncGenerator[AsyncSession, None]:
      async with async_session_factory() as session:
          yield session
  ```
- Never import the session factory directly in routers; always depend on
  `get_session`.
- Keep all SQL in the `crud/` layer — routers must not construct queries.

---

## Testing

- Test file per router module (see project structure above).
- Use an in-memory SQLite database for tests; create all tables in a session-scoped
  fixture defined in `conftest.py`.
- Use `httpx.AsyncClient` with `app` mounted directly — no live server required.
- Every endpoint must have at minimum:
  - A happy-path test.
  - A not-found / invalid-input test.
- Run tests with:
  ```bash
  pytest -v
  ```

---

## Running Locally

```bash
# Install dependencies
uv sync --extra dev

# Apply migrations
alembic upgrade head

# Start the development server
fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`.

---

## Common Commands

```bash
# Lint and auto-fix
ruff check . --fix
ruff format .

# Type check
mypy app/

# Generate a new migration after model changes
alembic revision --autogenerate -m "short description"

# Run tests with coverage
pytest --cov=app --cov-report=term-missing
```

---

## Out of Scope for MVP

The following are explicitly deferred — do not implement unless instructed:

- Authentication / user accounts
- Multi-currency support
- Recurring transactions
- Reporting / summary endpoints
- Pagination (return full result sets for now)