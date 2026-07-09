"""Async CRUD operations for the Budget domain."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Budget
from app.schemas import BudgetCopyResponse, BudgetCreate, BudgetUpdate


async def _get_or_404(session: AsyncSession, budget_id: int) -> Budget:
    """Fetch a budget by primary key or raise 404.

    Args:
        session: Active async database session.
        budget_id: Primary key of the budget to fetch.

    Returns:
        The Budget ORM instance with the given ID.

    Raises:
        HTTPException: With status 404 if no budget matches the ID.
    """
    result = await session.get(Budget, budget_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return result


async def get_all_budgets(session: AsyncSession) -> list[Budget]:
    """Return all budgets ordered by ID.

    Args:
        session: Active async database session.

    Returns:
        List of all Budget ORM instances.
    """
    result = await session.execute(select(Budget).order_by(Budget.id))
    return list(result.scalars().all())


async def get_budget(session: AsyncSession, budget_id: int) -> Budget:
    """Return a single budget by primary key.

    Args:
        session: Active async database session.
        budget_id: Primary key of the budget to fetch.

    Returns:
        The matching Budget ORM instance.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await _get_or_404(session, budget_id)


async def create_budget(session: AsyncSession, payload: BudgetCreate) -> Budget:
    """Persist a new budget and return the saved instance.

    Args:
        session: Active async database session.
        payload: Validated creation payload.

    Returns:
        The newly created Budget ORM instance with a populated ID.

    Raises:
        HTTPException: With status 409 if a budget for the same
            (category_id, month) already exists.
    """
    budget = Budget(
        category_id=payload.category_id,
        month=payload.month,
        limit_amount=payload.limit_amount,
    )
    session.add(budget)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                f"Budget for category {payload.category_id} in month "
                f"{payload.month} already exists"
            ),
        ) from exc
    await session.refresh(budget)
    return budget


async def update_budget(
    session: AsyncSession, budget_id: int, payload: BudgetUpdate
) -> Budget:
    """Update the limit amount on an existing budget.

    Args:
        session: Active async database session.
        budget_id: Primary key of the budget to update.
        payload: Validated update payload.

    Returns:
        The updated Budget ORM instance.

    Raises:
        HTTPException: With status 404 if not found.
    """
    budget = await _get_or_404(session, budget_id)
    budget.limit_amount = payload.limit_amount
    await session.commit()
    await session.refresh(budget)
    return budget


async def delete_budget(session: AsyncSession, budget_id: int) -> None:
    """Delete a budget by primary key.

    Args:
        session: Active async database session.
        budget_id: Primary key of the budget to delete.

    Raises:
        HTTPException: With status 404 if not found.
    """
    budget = await _get_or_404(session, budget_id)
    await session.delete(budget)
    await session.commit()


async def copy_budgets(
    session: AsyncSession,
    source_month: str,
    target_month: str,
) -> BudgetCopyResponse:
    """Copy all budgets from one month to another.

    Skips any category that already has a budget in the target month.
    Returns a count of copied rows and a list of skipped category IDs.

    Args:
        session: Active async database session.
        source_month: Month string (``"YYYY-MM"``) to copy budgets *from*.
        target_month: Month string (``"YYYY-MM"``) to copy budgets *to*.

    Returns:
        A BudgetCopyResponse with ``copied`` count and
        ``skipped_category_ids`` list.

    Raises:
        HTTPException: With status 404 if source_month has no budgets.
    """
    # Fetch all source budgets.
    source_result = await session.execute(
        select(Budget).where(Budget.month == source_month)
    )
    source_budgets = list(source_result.scalars().all())

    if not source_budgets:
        raise HTTPException(
            status_code=404,
            detail=f"No budgets found for month {source_month}",
        )

    # Fetch existing target category IDs to detect duplicates.
    target_result = await session.execute(
        select(Budget.category_id).where(Budget.month == target_month)
    )
    existing_target_ids = set(target_result.scalars().all())

    copied = 0
    skipped_category_ids: list[int] = []

    for source in source_budgets:
        if source.category_id in existing_target_ids:
            skipped_category_ids.append(source.category_id)
            continue
        new_budget = Budget(
            category_id=source.category_id,
            month=target_month,
            limit_amount=source.limit_amount,
        )
        session.add(new_budget)
        copied += 1

    await session.commit()

    return BudgetCopyResponse(copied=copied, skipped_category_ids=skipped_category_ids)
