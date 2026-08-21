"""Pydantic v2 request/response schemas for all three domains."""

from datetime import date as Date
from datetime import datetime as Datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


class CategoryCreate(BaseModel):
    """Schema for creating a new category.

    Attributes:
        name: Unique, non-null human-readable label.
        description: Optional longer description.
    """

    name: str = Field(..., min_length=1)
    description: str | None = None


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category.

    Attributes:
        name: New label for the category.
        description: New description; pass ``None`` to clear.
    """

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None


class CategoryResponse(BaseModel):
    """Schema returned by the API for a category resource.

    Attributes:
        id: Primary key.
        name: Human-readable label.
        description: Optional longer description.
        created_at: ISO-8601 timestamp of creation.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: Datetime


# ---------------------------------------------------------------------------
# Transaction
# ---------------------------------------------------------------------------

TransactionType = Literal["income", "expense", "savings"]


class TransactionCreate(BaseModel):
    """Schema for recording a new transaction.

    Attributes:
        amount: Positive monetary value.
        type: ``"income"`` or ``"expense"``.
        description: Optional free-text note.
        date: Calendar date; defaults to today.
        category_id: Optional FK to a category.
    """

    amount: float = Field(..., gt=0)
    type: TransactionType
    description: str | None = None
    date: Date = Field(default_factory=Date.today)
    category_id: int | None = None


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction.

    Attributes:
        amount: New positive monetary value.
        type: New transaction direction.
        description: New note; ``None`` clears it.
        date: New calendar date.
        category_id: New category FK; ``None`` removes assignment.
    """

    amount: float | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    description: str | None = None
    date: Date | None = None
    category_id: int | None = None


class TransactionResponse(BaseModel):
    """Schema returned by the API for a transaction resource.

    Attributes:
        id: Primary key.
        amount: Positive monetary value.
        type: ``"income"`` or ``"expense"``.
        description: Optional free-text note.
        date: Calendar date of the transaction.
        category_id: Optional FK to a category.
        created_at: ISO-8601 timestamp of creation.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    type: str
    description: str | None
    date: Date
    category_id: int | None
    created_at: Datetime


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------


class BudgetCreate(BaseModel):
    """Schema for creating a budget limit.

    Attributes:
        category_id: FK to the category this budget applies to.
        month: Month in ``"YYYY-MM"`` format.
        limit_amount: Maximum spending amount; must be > 0.
    """

    category_id: int
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    limit_amount: float = Field(..., gt=0)


class BudgetUpdate(BaseModel):
    """Schema for updating an existing budget.

    Attributes:
        limit_amount: New maximum spending amount; must be > 0.
    """

    limit_amount: float = Field(..., gt=0)


class BudgetResponse(BaseModel):
    """Schema returned by the API for a budget resource.

    Attributes:
        id: Primary key.
        category_id: FK to the associated category.
        month: Month in ``"YYYY-MM"`` format.
        limit_amount: Maximum spending amount.
        created_at: ISO-8601 timestamp of creation.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    month: str
    limit_amount: float
    created_at: Datetime


class BudgetCopyRequest(BaseModel):
    """Schema for the budget copy operation.

    Attributes:
        source_month: Month to copy budgets *from*, in ``"YYYY-MM"`` format.
        target_month: Month to copy budgets *to*, in ``"YYYY-MM"`` format.
    """

    source_month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    target_month: str = Field(..., pattern=r"^\d{4}-\d{2}$")


# ---------------------------------------------------------------------------
# Spending summary
# ---------------------------------------------------------------------------


class SpendingCategoryBreakdown(BaseModel):
    """Spending total for a single category.

    Attributes:
        category: Category name, or ``"Uncategorized"`` for transactions with
            no assigned category.
        total: Sum of expense amounts in this category.
    """

    category: str
    total: float


class SpendingResponse(BaseModel):
    """Aggregated spending summary for a date range.

    Attributes:
        period_start: Inclusive start of the queried period.
        period_end: Inclusive end of the queried period.
        total: Total expense amount across all matching transactions.
        breakdown: Per-category totals, ordered by amount descending.
    """

    period_start: Date
    period_end: Date
    total: float
    breakdown: list[SpendingCategoryBreakdown]


class BudgetCopyResponse(BaseModel):
    """Schema returned after a budget copy operation.

    Attributes:
        copied: Number of budget rows successfully copied.
        skipped_category_ids: Category IDs that were skipped due to existing
            budgets in the target month.
    """

    copied: int
    skipped_category_ids: list[int]
