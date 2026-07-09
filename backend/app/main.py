"""FastAPI application factory with lifespan management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import budgets, categories, transactions


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Creates all database tables on startup for development convenience.
    Disposes of the engine connection pool on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to the application while it is running.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application.

    Registers all domain routers under the ``/api/v1`` prefix.

    Returns:
        A fully configured FastAPI application instance.
    """
    app = FastAPI(
        title="Budgetah API",
        description="Personal budget REST API",
        version="0.1.0",
        lifespan=lifespan,
    )

    api_prefix = "/api/v1"
    app.include_router(categories.router, prefix=api_prefix)
    app.include_router(transactions.router, prefix=api_prefix)
    app.include_router(budgets.router, prefix=api_prefix)

    return app


app = create_app()
