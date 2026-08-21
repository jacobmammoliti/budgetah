"""FastAPI router for transaction CRUD endpoints."""

from datetime import date as Date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session
from app.schemas import (
    SpendingCategoryBreakdown,
    SpendingResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionType,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(
    session: SessionDep,
    type: Annotated[TransactionType | None, Query()] = None,
    category_id: Annotated[int | None, Query()] = None,
    start_date: Annotated[Date | None, Query()] = None,
    end_date: Annotated[Date | None, Query()] = None,
) -> list[TransactionResponse]:
    """List transactions with optional filters.

    Args:
        session: Injected async database session.
        type: Filter to ``"income"`` or ``"expense"`` only.
        category_id: Filter to a specific category.
        start_date: Only return transactions on or after this date.
        end_date: Only return transactions on or before this date.

    Returns:
        A filtered list of transaction resources.
    """
    return await crud.transactions.get_all_transactions(  # type: ignore[return-value]
        session,
        type_filter=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    payload: TransactionCreate, session: SessionDep
) -> TransactionResponse:
    """Record a new transaction.

    Args:
        payload: Validated transaction creation data.
        session: Injected async database session.

    Returns:
        The newly created transaction resource.
    """
    return await crud.transactions.create_transaction(session, payload)  # type: ignore[return-value]


@router.get("/spending", response_model=SpendingResponse)
async def get_spending(
    session: SessionDep,
    start_date: Annotated[Date, Query()],
    end_date: Annotated[Date, Query()],
    category: Annotated[str | None, Query()] = None,
) -> SpendingResponse:
    """Return expense spending grouped by category for a date range.

    Args:
        session: Injected async database session.
        start_date: Inclusive start date (``YYYY-MM-DD``).
        end_date: Inclusive end date (``YYYY-MM-DD``).
        category: Case-insensitive category name filter. When omitted all
            categories are included.

    Returns:
        Aggregated spending with a per-category breakdown.
    """
    total, breakdown = await crud.transactions.get_spending_by_category(
        session,
        start_date=start_date,
        end_date=end_date,
        category_name=category,
    )
    return SpendingResponse(
        period_start=start_date,
        period_end=end_date,
        total=total,
        breakdown=[
            SpendingCategoryBreakdown(category=name, total=amount)
            for name, amount in breakdown
        ],
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int, session: SessionDep
) -> TransactionResponse:
    """Retrieve a single transaction by ID.

    Args:
        transaction_id: Primary key of the transaction to fetch.
        session: Injected async database session.

    Returns:
        The matching transaction resource.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await crud.transactions.get_transaction(session, transaction_id)  # type: ignore[return-value]


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int, payload: TransactionUpdate, session: SessionDep
) -> TransactionResponse:
    """Update an existing transaction.

    Args:
        transaction_id: Primary key of the transaction to update.
        payload: Partial update payload; unset fields are ignored.
        session: Injected async database session.

    Returns:
        The updated transaction resource.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await crud.transactions.update_transaction(  # type: ignore[return-value]
        session, transaction_id, payload
    )


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: int, session: SessionDep) -> None:
    """Delete a transaction by ID.

    Args:
        transaction_id: Primary key of the transaction to delete.
        session: Injected async database session.

    Raises:
        HTTPException: With status 404 if not found.
    """
    await crud.transactions.delete_transaction(session, transaction_id)
