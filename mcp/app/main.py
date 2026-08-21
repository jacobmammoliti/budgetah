"""Budgetah MCP server."""

import calendar
import os
from datetime import date as Date

import httpx
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

mcp = FastMCP("budgetah")

@mcp.tool
async def list_categories() -> list[dict]:
    """Return all available budget categories."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/categories/")
        response.raise_for_status()
        return response.json()

@mcp.tool
async def query_spending(
    month: str,
    category: str | None = None,
) -> dict:
    """Return expense spending for a given month, optionally filtered by category.

    Use this tool to answer questions like "How much have I spent on groceries
    in July?" or "Break down my spending in July 2026."

    Args:
        month: The month to query in ``"YYYY-MM"`` format (e.g. ``"2026-07"``).
        category: Optional category name to filter by (e.g. ``"Groceries"``).
            When omitted, all categories are returned.

    Returns:
        A dict with ``period_start``, ``period_end``, ``total``, and
        ``breakdown`` — a list of ``{category, total}`` objects ordered by
        amount descending.
    """
    try:
        year, month_num = int(month[:4]), int(month[5:7])
    except (ValueError, IndexError):
        return {"error": f"Invalid month format '{month}'. Expected 'YYYY-MM'."}

    start_date = Date(year, month_num, 1)
    last_day = calendar.monthrange(year, month_num)[1]
    end_date = Date(year, month_num, last_day)

    params: dict[str, str] = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    if category is not None:
        params["category"] = category

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/transactions/spending", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool
async def list_transactions_for_category(
    month: str,
    category: str,
) -> dict:
    """Return individual expense transactions for a category in a given month.

    Use this tool to answer questions like "Give me a breakdown of my grocery
    spending in July" where the user wants each transaction's amount and
    description, not just a total.

    Args:
        month: The month to query in ``"YYYY-MM"`` format (e.g. ``"2026-07"``).
        category: Category name to filter by (e.g. ``"Groceries"``).

    Returns:
        A dict with ``category``, ``period_start``, ``period_end``, ``total``,
        and ``transactions`` — a list of ``{date, amount, description}`` objects
        ordered by date descending.
    """
    try:
        year, month_num = int(month[:4]), int(month[5:7])
    except (ValueError, IndexError):
        return {"error": f"Invalid month format '{month}'. Expected 'YYYY-MM'."}

    start_date = Date(year, month_num, 1)
    last_day = calendar.monthrange(year, month_num)[1]
    end_date = Date(year, month_num, last_day)

    async with httpx.AsyncClient() as client:
        categories_response = await client.get(f"{BASE_URL}/categories/")
        categories_response.raise_for_status()
        categories = categories_response.json()

    match = next(
        (c for c in categories if c["name"].lower() == category.lower()),
        None,
    )
    if match is None:
        return {"error": f"Category '{category}' not found."}

    async with httpx.AsyncClient() as client:
        txn_response = await client.get(
            f"{BASE_URL}/transactions/",
            params={
                "type": "expense",
                "category_id": match["id"],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )
        txn_response.raise_for_status()
        transactions = txn_response.json()

    total = sum(t["amount"] for t in transactions)
    return {
        "category": match["name"],
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "total": total,
        "transactions": [
            {"date": t["date"], "amount": t["amount"], "description": t["description"]}
            for t in transactions
        ],
    }


app = mcp.http_app(transport="streamable-http")
# TODO: Tighten up CORS
app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id"],
)