"""Tests for the /api/v1/categories endpoints."""

import pytest
from httpx import AsyncClient

BASE = "/api/v1/categories"


@pytest.mark.asyncio
async def test_list_categories_empty(client: AsyncClient) -> None:
    """GET /categories returns an empty list when no categories exist."""
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_category_happy_path(client: AsyncClient) -> None:
    """POST /categories creates and returns a new category."""
    payload = {"name": "Groceries", "description": "Food and household items"}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Groceries"
    assert data["description"] == "Food and household items"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_category_no_description(client: AsyncClient) -> None:
    """POST /categories works without an optional description."""
    payload = {"name": "Utilities"}
    response = await client.post(f"{BASE}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Utilities"
    assert data["description"] is None


@pytest.mark.asyncio
async def test_list_categories_after_create(client: AsyncClient) -> None:
    """GET /categories lists all created categories."""
    await client.post(f"{BASE}/", json={"name": "Transport"})
    await client.post(f"{BASE}/", json={"name": "Entertainment"})
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Transport" in names
    assert "Entertainment" in names


@pytest.mark.asyncio
async def test_get_category_happy_path(client: AsyncClient) -> None:
    """GET /categories/{id} returns the correct category."""
    create_resp = await client.post(f"{BASE}/", json={"name": "Rent"})
    category_id = create_resp.json()["id"]
    response = await client.get(f"{BASE}/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Rent"


@pytest.mark.asyncio
async def test_get_category_not_found(client: AsyncClient) -> None:
    """GET /categories/{id} returns 404 for a non-existent ID."""
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_category_happy_path(client: AsyncClient) -> None:
    """PUT /categories/{id} updates the category fields."""
    create_resp = await client.post(f"{BASE}/", json={"name": "Healthcare"})
    category_id = create_resp.json()["id"]
    response = await client.put(
        f"{BASE}/{category_id}",
        json={"name": "Medical", "description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Medical"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_category_not_found(client: AsyncClient) -> None:
    """PUT /categories/{id} returns 404 for a non-existent ID."""
    response = await client.put(f"{BASE}/99999", json={"name": "Ghost"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_happy_path(client: AsyncClient) -> None:
    """DELETE /categories/{id} removes the category and returns 204."""
    create_resp = await client.post(f"{BASE}/", json={"name": "ToDelete"})
    category_id = create_resp.json()["id"]
    response = await client.delete(f"{BASE}/{category_id}")
    assert response.status_code == 204
    # Verify it's gone.
    get_resp = await client.get(f"{BASE}/{category_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_not_found(client: AsyncClient) -> None:
    """DELETE /categories/{id} returns 404 for a non-existent ID."""
    response = await client.delete(f"{BASE}/99999")
    assert response.status_code == 404
