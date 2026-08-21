"""Tests for the /api/v1/budgets endpoints."""

import pytest
from httpx import AsyncClient

BASE = "/api/v1/budgets"
CATS = "/api/v1/categories"


async def _make_category(client: AsyncClient, name: str) -> int:
    """Helper to create a category and return its ID.

    Args:
        client: HTTP test client.
        name: Category name to create.

    Returns:
        The primary key of the newly created category.
    """
    resp = await client.post(f"{CATS}/", json={"name": name})
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_budgets_empty(client: AsyncClient) -> None:
    """GET /budgets returns an empty list when none exist."""
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_budget_happy_path(client: AsyncClient) -> None:
    """POST /budgets creates a budget and returns 201."""
    cat_id = await _make_category(client, "HousingBudget")
    payload = {"category_id": cat_id, "month": "2025-07", "limit_amount": 1500.00}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] == cat_id
    assert data["month"] == "2025-07"
    assert data["limit_amount"] == 1500.00


@pytest.mark.asyncio
async def test_create_budget_duplicate_returns_409(client: AsyncClient) -> None:
    """POST /budgets returns 409 on duplicate (category_id, month)."""
    cat_id = await _make_category(client, "DupCategory")
    payload = {"category_id": cat_id, "month": "2025-08", "limit_amount": 200.0}
    await client.post(f"{BASE}/", json=payload)
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_budget_invalid_limit(client: AsyncClient) -> None:
    """POST /budgets rejects limit_amount <= 0."""
    cat_id = await _make_category(client, "BadLimit")
    payload = {"category_id": cat_id, "month": "2025-09", "limit_amount": -50.0}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_budget_happy_path(client: AsyncClient) -> None:
    """GET /budgets/{id} returns the correct budget."""
    cat_id = await _make_category(client, "GetBudget")
    create_resp = await client.post(
        f"{BASE}/",
        json={"category_id": cat_id, "month": "2025-10", "limit_amount": 300.0},
    )
    budget_id = create_resp.json()["id"]
    response = await client.get(f"{BASE}/{budget_id}")
    assert response.status_code == 200
    assert response.json()["id"] == budget_id


@pytest.mark.asyncio
async def test_get_budget_not_found(client: AsyncClient) -> None:
    """GET /budgets/{id} returns 404 for a non-existent ID."""
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_budget_happy_path(client: AsyncClient) -> None:
    """DELETE /budgets/{id} removes the budget and returns 204."""
    cat_id = await _make_category(client, "DelBudget")
    create_resp = await client.post(
        f"{BASE}/",
        json={"category_id": cat_id, "month": "2025-11", "limit_amount": 100.0},
    )
    budget_id = create_resp.json()["id"]
    response = await client.delete(f"{BASE}/{budget_id}")
    assert response.status_code == 204
    assert (await client.get(f"{BASE}/{budget_id}")).status_code == 404


@pytest.mark.asyncio
async def test_delete_budget_not_found(client: AsyncClient) -> None:
    """DELETE /budgets/{id} returns 404 for a non-existent ID."""
    response = await client.delete(f"{BASE}/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Copy endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_copy_budgets_happy_path(client: AsyncClient) -> None:
    """POST /budgets/copy copies all source budgets to the target month."""
    cat_a = await _make_category(client, "CopyA")
    cat_b = await _make_category(client, "CopyB")
    await client.post(
        f"{BASE}/",
        json={"category_id": cat_a, "month": "2025-06", "limit_amount": 400.0},
    )
    await client.post(
        f"{BASE}/",
        json={"category_id": cat_b, "month": "2025-06", "limit_amount": 600.0},
    )
    response = await client.post(
        f"{BASE}/copy",
        json={"source_month": "2025-06", "target_month": "2025-07"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["copied"] == 2
    assert data["skipped_category_ids"] == []


@pytest.mark.asyncio
async def test_copy_budgets_skips_existing(client: AsyncClient) -> None:
    """POST /budgets/copy skips categories already present in target month."""
    cat_a = await _make_category(client, "SkipA")
    cat_b = await _make_category(client, "SkipB")
    # Source
    await client.post(
        f"{BASE}/",
        json={"category_id": cat_a, "month": "2026-01", "limit_amount": 200.0},
    )
    await client.post(
        f"{BASE}/",
        json={"category_id": cat_b, "month": "2026-01", "limit_amount": 300.0},
    )
    # Pre-existing target for cat_a
    await client.post(
        f"{BASE}/",
        json={"category_id": cat_a, "month": "2026-02", "limit_amount": 999.0},
    )
    response = await client.post(
        f"{BASE}/copy",
        json={"source_month": "2026-01", "target_month": "2026-02"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["copied"] == 1
    assert cat_a in data["skipped_category_ids"]


@pytest.mark.asyncio
async def test_copy_budgets_source_not_found(client: AsyncClient) -> None:
    """POST /budgets/copy returns 404 when source month has no budgets."""
    response = await client.post(
        f"{BASE}/copy",
        json={"source_month": "1999-01", "target_month": "1999-02"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_copy_budgets_same_month_returns_422(client: AsyncClient) -> None:
    """POST /budgets/copy returns 422 when source and target months are equal."""
    response = await client.post(
        f"{BASE}/copy",
        json={"source_month": "2025-06", "target_month": "2025-06"},
    )
    assert response.status_code == 422
