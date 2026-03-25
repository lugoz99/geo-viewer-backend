from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.db import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services import user
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    created_user = await service.create_user(user)
    return created_user


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    users = await service.get_all_users()
    return users


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return user


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    updated_user = await service.update_user(user_id, user_data)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await service.delete_user(user_id)
