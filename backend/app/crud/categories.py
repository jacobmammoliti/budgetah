"""Async CRUD operations for the Category domain."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


async def _get_or_404(session: AsyncSession, category_id: int) -> Category:
    """Fetch a category by primary key or raise 404.

    Args:
        session: Active async database session.
        category_id: Primary key of the category to fetch.

    Returns:
        The Category ORM instance with the given ID.

    Raises:
        HTTPException: With status 404 if no category matches the ID.
    """
    result = await session.get(Category, category_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return result


async def get_all_categories(session: AsyncSession) -> list[Category]:
    """Return all categories ordered by ID.

    Args:
        session: Active async database session.

    Returns:
        List of all Category ORM instances.
    """
    result = await session.execute(select(Category).order_by(Category.id))
    return list(result.scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category:
    """Return a single category by primary key.

    Args:
        session: Active async database session.
        category_id: Primary key of the category to fetch.

    Returns:
        The matching Category ORM instance.

    Raises:
        HTTPException: With status 404 if not found.
    """
    return await _get_or_404(session, category_id)


async def create_category(session: AsyncSession, payload: CategoryCreate) -> Category:
    """Persist a new category and return the saved instance.

    Args:
        session: Active async database session.
        payload: Validated creation payload.

    Returns:
        The newly created Category ORM instance with a populated ID.
    """
    category = Category(name=payload.name, description=payload.description)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(
    session: AsyncSession, category_id: int, payload: CategoryUpdate
) -> Category:
    """Apply partial updates to an existing category.

    Args:
        session: Active async database session.
        category_id: Primary key of the category to update.
        payload: Validated update payload; ``None`` fields are ignored.

    Returns:
        The updated Category ORM instance.

    Raises:
        HTTPException: With status 404 if not found.
    """
    category = await _get_or_404(session, category_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(category, field, value)
    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category_id: int) -> None:
    """Delete a category by primary key.

    Args:
        session: Active async database session.
        category_id: Primary key of the category to delete.

    Raises:
        HTTPException: With status 404 if not found.
    """
    category = await _get_or_404(session, category_id)
    await session.delete(category)
    await session.commit()
