"""FastAPI router for budget CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session
from app.schemas import (
    BudgetCopyRequest,
    BudgetCopyResponse,
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
)

router = APIRouter(prefix="/budgets", tags=["budgets"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[BudgetResponse])
async def list_budgets(session: SessionDep) -> list[BudgetResponse]:
    """List all budgets.

    Args:
        session: Injected async database session.

    Returns:
        A list of all budget resources.
    """
    return await crud.budgets.get_all_budgets(session)  # type: ignore[return-value]


@router.post("/copy", response_model=BudgetCopyResponse, status_code=200)
async def copy_budgets(
    payload: BudgetCopyRequest, session: SessionDep
) -> BudgetCopyResponse:
    """Copy budgets from one month to another.

    Skips categories that already have a budget in the target month.
    Returns counts of copied and skipped entries.

    Args:
        payload: Source and target month for the copy operation.
        session: Injected async database session.

    Returns:
        A BudgetCopyResponse with ``copied`` count and
        ``skipped_category_ids`` list.

    Raises:
        HTTPException: With status 422 if source and target months are equal.
        HTTPException: With status 404 if source month has no budgets.
    """
    if payload.source_month == payload.target_month:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="source_month and target_month must be different",
        )
    return await crud.budgets.copy_budgets(
        session, payload.source_month, payload.target_month
    )


@router.post("/", response_model=BudgetResponse, status_code=201)
async def create_budget(payload: BudgetCreate, session: SessionDep) -> BudgetResponse:
    """Create a new budget limit for a category/month combination.

    Args:
        payload: Validated budget creation data.
        session: Injected async database session.

    Returns:
        The newly created budget resource.

    Raises:
        HTTPException: With status 409 if a budget already exists for
            the given category and month.
    """
    return await crud.budgets.create_budget(session, payload)  # type: ignore[return-value]


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, session: SessionDep) -> BudgetResponse:
    """Retrieve a single budget by ID.

    Args:
        budget_id: Primary key of the budget to fetch.
        session: Injected async database session.

    Returns:
        The matching budget resource.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await crud.budgets.get_budget(session, budget_id)  # type: ignore[return-value]


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int, payload: BudgetUpdate, session: SessionDep
) -> BudgetResponse:
    """Update the limit amount for an existing budget.

    Args:
        budget_id: Primary key of the budget to update.
        payload: Validated update payload containing the new limit_amount.
        session: Injected async database session.

    Returns:
        The updated budget resource.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await crud.budgets.update_budget(session, budget_id, payload)  # type: ignore[return-value]


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(budget_id: int, session: SessionDep) -> None:
    """Delete a budget by ID.

    Args:
        budget_id: Primary key of the budget to delete.
        session: Injected async database session.

    Raises:
        HTTPException: With status 404 if not found.
    """
    await crud.budgets.delete_budget(session, budget_id)
