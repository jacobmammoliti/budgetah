"""Tests for the /api/v1/transactions endpoints."""

import pytest
from httpx import AsyncClient

BASE = "/api/v1/transactions"
CATS = "/api/v1/categories"


@pytest.mark.asyncio
async def test_list_transactions_empty(client: AsyncClient) -> None:
    """GET /transactions returns an empty list when no transactions exist."""
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_transaction_income(client: AsyncClient) -> None:
    """POST /transactions creates an income transaction successfully."""
    payload = {"amount": 2500.00, "type": "income", "date": "2025-06-01"}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 2500.00
    assert data["type"] == "income"
    assert data["date"] == "2025-06-01"
    assert data["category_id"] is None


@pytest.mark.asyncio
async def test_create_transaction_expense(client: AsyncClient) -> None:
    """POST /transactions creates an expense transaction successfully."""
    payload = {
        "amount": 75.50,
        "type": "expense",
        "description": "Grocery run",
        "date": "2025-06-15",
    }
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 75.50
    assert data["type"] == "expense"
    assert data["description"] == "Grocery run"


@pytest.mark.asyncio
async def test_create_transaction_with_category(client: AsyncClient) -> None:
    """POST /transactions accepts a valid category_id."""
    cat_resp = await client.post(f"{CATS}/", json={"name": "Food"})
    cat_id = cat_resp.json()["id"]
    payload = {
        "amount": 42.00,
        "type": "expense",
        "date": "2025-06-20",
        "category_id": cat_id,
    }
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 201
    assert response.json()["category_id"] == cat_id


@pytest.mark.asyncio
async def test_create_transaction_invalid_amount(client: AsyncClient) -> None:
    """POST /transactions rejects amount <= 0."""
    payload = {"amount": -10.00, "type": "expense", "date": "2025-06-01"}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_transaction_zero_amount(client: AsyncClient) -> None:
    """POST /transactions rejects amount equal to 0."""
    payload = {"amount": 0, "type": "expense", "date": "2025-06-01"}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_transaction_invalid_type(client: AsyncClient) -> None:
    """POST /transactions rejects an invalid transaction type."""
    payload = {"amount": 10.00, "type": "transfer", "date": "2025-06-01"}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_transaction_happy_path(client: AsyncClient) -> None:
    """GET /transactions/{id} returns the correct transaction."""
    create_resp = await client.post(
        f"{BASE}/", json={"amount": 100.0, "type": "income", "date": "2025-01-01"}
    )
    tx_id = create_resp.json()["id"]
    response = await client.get(f"{BASE}/{tx_id}")
    assert response.status_code == 200
    assert response.json()["id"] == tx_id


@pytest.mark.asyncio
async def test_get_transaction_not_found(client: AsyncClient) -> None:
    """GET /transactions/{id} returns 404 for a non-existent ID."""
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_transaction_happy_path(client: AsyncClient) -> None:
    """PUT /transactions/{id} updates the transaction amount."""
    create_resp = await client.post(
        f"{BASE}/", json={"amount": 50.0, "type": "expense", "date": "2025-03-10"}
    )
    tx_id = create_resp.json()["id"]
    response = await client.put(f"{BASE}/{tx_id}", json={"amount": 99.99})
    assert response.status_code == 200
    assert response.json()["amount"] == 99.99


@pytest.mark.asyncio
async def test_update_transaction_not_found(client: AsyncClient) -> None:
    """PUT /transactions/{id} returns 404 for a non-existent ID."""
    response = await client.put(f"{BASE}/99999", json={"amount": 10.0})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_transaction_happy_path(client: AsyncClient) -> None:
    """DELETE /transactions/{id} removes the transaction and returns 204."""
    create_resp = await client.post(
        f"{BASE}/", json={"amount": 10.0, "type": "expense", "date": "2025-02-01"}
    )
    tx_id = create_resp.json()["id"]
    response = await client.delete(f"{BASE}/{tx_id}")
    assert response.status_code == 204
    assert (await client.get(f"{BASE}/{tx_id}")).status_code == 404


@pytest.mark.asyncio
async def test_delete_transaction_not_found(client: AsyncClient) -> None:
    """DELETE /transactions/{id} returns 404 for a non-existent ID."""
    response = await client.delete(f"{BASE}/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_filter_by_type(client: AsyncClient) -> None:
    """GET /transactions?type= filters correctly by transaction type."""
    await client.post(
        f"{BASE}/", json={"amount": 1.0, "type": "income", "date": "2025-04-01"}
    )
    await client.post(
        f"{BASE}/", json={"amount": 2.0, "type": "expense", "date": "2025-04-02"}
    )
    resp = await client.get(f"{BASE}/", params={"type": "income"})
    assert resp.status_code == 200
    assert all(t["type"] == "income" for t in resp.json())


@pytest.mark.asyncio
async def test_filter_by_category_id(client: AsyncClient) -> None:
    """GET /transactions?category_id= filters to the specified category."""
    cat_resp = await client.post(f"{CATS}/", json={"name": "TravelFilter"})
    cat_id = cat_resp.json()["id"]
    await client.post(
        f"{BASE}/",
        json={
            "amount": 300.0,
            "type": "expense",
            "date": "2025-05-01",
            "category_id": cat_id,
        },
    )
    await client.post(
        f"{BASE}/", json={"amount": 50.0, "type": "expense", "date": "2025-05-02"}
    )
    resp = await client.get(f"{BASE}/", params={"category_id": cat_id})
    assert resp.status_code == 200
    assert all(t["category_id"] == cat_id for t in resp.json())


@pytest.mark.asyncio
async def test_filter_by_date_range(client: AsyncClient) -> None:
    """GET /transactions with start_date/end_date returns only matching rows."""
    await client.post(
        f"{BASE}/", json={"amount": 10.0, "type": "expense", "date": "2025-01-05"}
    )
    await client.post(
        f"{BASE}/", json={"amount": 20.0, "type": "expense", "date": "2025-06-15"}
    )
    await client.post(
        f"{BASE}/", json={"amount": 30.0, "type": "expense", "date": "2025-12-31"}
    )
    resp = await client.get(
        f"{BASE}/",
        params={"start_date": "2025-06-01", "end_date": "2025-06-30"},
    )
    assert resp.status_code == 200
    dates = [t["date"] for t in resp.json()]
    assert "2025-06-15" in dates
    assert "2025-01-05" not in dates
    assert "2025-12-31" not in dates
