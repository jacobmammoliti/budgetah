"""FastAPI router for category CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(session: SessionDep) -> list[CategoryResponse]:
    """List all categories.

    Args:
        session: Injected async database session.

    Returns:
        A list of all category resources.
    """
    return await crud.categories.get_all_categories(session)  # type: ignore[return-value]


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    payload: CategoryCreate, session: SessionDep
) -> CategoryResponse:
    """Create a new category.

    Args:
        payload: Validated category creation data.
        session: Injected async database session.

    Returns:
        The newly created category resource.
    """
    return await crud.categories.create_category(session, payload)  # type: ignore[return-value]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, session: SessionDep) -> CategoryResponse:
    """Retrieve a single category by ID.

    Args:
        category_id: Primary key of the category to fetch.
        session: Injected async database session.

    Returns:
        The matching category resource.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await crud.categories.get_category(session, category_id)  # type: ignore[return-value]


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int, payload: CategoryUpdate, session: SessionDep
) -> CategoryResponse:
    """Update an existing category.

    Args:
        category_id: Primary key of the category to update.
        payload: Partial update payload; unset fields are ignored.
        session: Injected async database session.

    Returns:
        The updated category resource.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await crud.categories.update_category(session, category_id, payload)  # type: ignore[return-value]


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: SessionDep) -> None:
    """Delete a category by ID.

    Args:
        category_id: Primary key of the category to delete.
        session: Injected async database session.

    Raises:
        HTTPException: With status 404 if not found.
    """
    await crud.categories.delete_category(session, category_id)
