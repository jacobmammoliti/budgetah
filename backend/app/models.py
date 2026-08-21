"""SQLAlchemy 2.x ORM models for the budget API."""

from datetime import date, datetime

from sqlalchemy import (
    DATE,
    DATETIME,
    REAL,
    TEXT,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Category(Base):
    """A named grouping for transactions (e.g., 'Groceries', 'Rent').

    Attributes:
        id: Auto-increment primary key.
        name: Unique, non-null human-readable label.
        description: Optional longer description.
        created_at: Timestamp set automatically on insert.
        transactions: Back-reference to associated transactions.
        budgets: Back-reference to associated budget limits.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME, server_default=func.now(), nullable=False
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category"
    )
    budgets: Mapped[list["Budget"]] = relationship("Budget", back_populates="category")


class Transaction(Base):
    """A single income or expense event.

    Attributes:
        id: Auto-increment primary key.
        amount: Positive monetary value; direction is conveyed by `type`.
        type: Either ``"income"`` or ``"expense"``.
        description: Optional free-text note.
        date: Calendar date of the transaction; defaults to today.
        category_id: Optional FK to :class:`Category`.
        created_at: Timestamp set automatically on insert.
        category: Related Category ORM object.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(REAL, nullable=False)
    type: Mapped[str] = mapped_column(TEXT, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    date: Mapped[date] = mapped_column(DATE, nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME, server_default=func.now(), nullable=False
    )

    category: Mapped[Category | None] = relationship(
        "Category", back_populates="transactions"
    )


class Budget(Base):
    """A spending limit for a category in a given calendar month.

    Attributes:
        id: Auto-increment primary key.
        category_id: FK to :class:`Category`.
        month: Month in ``"YYYY-MM"`` format.
        limit_amount: Maximum spending amount; must be greater than zero.
        created_at: Timestamp set automatically on insert.
        category: Related Category ORM object.
    """

    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint("category_id", "month", name="uq_budget_category_month"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    month: Mapped[str] = mapped_column(TEXT, nullable=False)
    limit_amount: Mapped[float] = mapped_column(REAL, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME, server_default=func.now(), nullable=False
    )

    category: Mapped[Category] = relationship("Category", back_populates="budgets")
