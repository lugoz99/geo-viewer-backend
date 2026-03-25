import pytest


# CREATE
@pytest.mark.asyncio
async def test_create_user(async_client):
    user = {
        "full_name": "John Doe",  # ← "name" → "full_name"
        "email": "john@test.com",
        "company_name": "TestCo",
        "hashed_password": "123",
    }

    response = await async_client.post("/api/v1/users/", json=user)

    assert response.status_code == 201
    assert response.json()["email"] == user["email"]


# GET ALL
@pytest.mark.asyncio
async def test_get_users(async_client):
    response = await async_client.get("/api/v1/users/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# DELETE
@pytest.mark.asyncio
async def test_delete_user(async_client):
    user = {
        "full_name": "Delete Me",  # ← "name" → "full_name"
        "email": "delete@test.com",
        "company_name": "TestCo2",
        "hashed_password": "123",
    }

    create = await async_client.post("/api/v1/users/", json=user)
    user_id = create.json()["id"]

    delete = await async_client.delete(f"/api/v1/users/{user_id}")

    assert delete.status_code == 204


# DUPLICATE COMPANY
@pytest.mark.asyncio
async def test_duplicate_company_name(async_client):
    user = {
        "full_name": "John Doe",  # ← "name" → "full_name"
        "email": "john1@test.com",
        "company_name": "UniqueCo",
        "hashed_password": "123",
    }

    response1 = await async_client.post("/api/v1/users/", json=user)
    assert response1.status_code == 201

    user2 = user.copy()
    user2["email"] = "john2@test.com"

    response2 = await async_client.post("/api/v1/users/", json=user2)

    assert response2.status_code in (400, 409)
