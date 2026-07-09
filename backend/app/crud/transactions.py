"""Async CRUD operations for the Transaction domain."""

from datetime import date as Date

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Transaction
from app.schemas import TransactionCreate, TransactionType, TransactionUpdate


async def _get_or_404(session: AsyncSession, transaction_id: int) -> Transaction:
    """Fetch a transaction by primary key or raise 404.

    Args:
        session: Active async database session.
        transaction_id: Primary key of the transaction to fetch.

    Returns:
        The Transaction ORM instance with the given ID.

    Raises:
        HTTPException: With status 404 if no transaction matches the ID.
    """
    result = await session.get(Transaction, transaction_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result


async def get_all_transactions(
    session: AsyncSession,
    type_filter: TransactionType | None = None,
    category_id: int | None = None,
    start_date: Date | None = None,
    end_date: Date | None = None,
) -> list[Transaction]:
    """Return transactions, optionally filtered by various criteria.

    Args:
        session: Active async database session.
        type_filter: Restrict to ``"income"`` or ``"expense"`` transactions.
        category_id: Restrict to transactions belonging to this category.
        start_date: Only include transactions on or after this date.
        end_date: Only include transactions on or before this date.

    Returns:
        List of matching Transaction ORM instances ordered by date descending.
    """
    stmt = select(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc())

    if type_filter is not None:
        stmt = stmt.where(Transaction.type == type_filter)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if start_date is not None:
        stmt = stmt.where(Transaction.date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.date <= end_date)

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_spending_by_category(
    session: AsyncSession,
    start_date: Date,
    end_date: Date,
    category_name: str | None = None,
) -> tuple[float, list[tuple[str, float]]]:
    """Return total expense spending grouped by category for a date range.

    Args:
        session: Active async database session.
        start_date: Inclusive start date for the period.
        end_date: Inclusive end date for the period.
        category_name: Case-insensitive category name to filter by. When
            ``None`` all categories (including uncategorized) are returned.

    Returns:
        A tuple of ``(total, breakdown)`` where ``total`` is the overall
        expense amount and ``breakdown`` is a list of
        ``(category_name, amount)`` pairs ordered by amount descending.
        Transactions with no category appear under ``"Uncategorized"``.
    """
    category_label = func.coalesce(Category.name, "Uncategorized")

    stmt = (
        select(category_label, func.sum(Transaction.amount).label("total"))
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(Transaction.type == "expense")
        .where(Transaction.date >= start_date)
        .where(Transaction.date <= end_date)
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    )

    if category_name is not None:
        stmt = stmt.where(func.lower(Category.name) == category_name.lower())

    result = await session.execute(stmt)
    rows = result.all()
    breakdown = [(str(row[0]), float(row[1])) for row in rows]
    total = sum(amount for _, amount in breakdown)
    return total, breakdown


async def get_transaction(session: AsyncSession, transaction_id: int) -> Transaction:
    """Return a single transaction by primary key.

    Args:
        session: Active async database session.
        transaction_id: Primary key of the transaction to fetch.

    Returns:
        The matching Transaction ORM instance.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await _get_or_404(session, transaction_id)


async def create_transaction(
    session: AsyncSession, payload: TransactionCreate
) -> Transaction:
    """Persist a new transaction and return the saved instance.

    Args:
        session: Active async database session.
        payload: Validated creation payload.

    Returns:
        The newly created Transaction ORM instance with a populated ID.
    """
    transaction = Transaction(
        amount=payload.amount,
        type=payload.type,
        description=payload.description,
        date=payload.date,
        category_id=payload.category_id,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


async def update_transaction(
    session: AsyncSession, transaction_id: int, payload: TransactionUpdate
) -> Transaction:
    """Apply partial updates to an existing transaction.

    Args:
        session: Active async database session.
        transaction_id: Primary key of the transaction to update.
        payload: Validated update payload; ``None`` fields are ignored.

    Returns:
        The updated Transaction ORM instance.

    Raises:
        HTTPException: With status 404 if not found.
    """
    transaction = await _get_or_404(session, transaction_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(transaction, field, value)
    await session.commit()
    await session.refresh(transaction)
    return transaction


async def delete_transaction(session: AsyncSession, transaction_id: int) -> None:
    """Delete a transaction by primary key.

    Args:
        session: Active async database session.
        transaction_id: Primary key of the transaction to delete.

    Raises:
        HTTPException: With status 404 if not found.
    """
    transaction = await _get_or_404(session, transaction_id)
    await session.delete(transaction)
    await session.commit()
