from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.db import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user import UserService

# Create router for user endpoints
router = APIRouter(prefix="/users", tags=["Users"])


# Create new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add one user"""
    service = UserService(db)
    created_user = await service.create_user(user)
    return created_user


# Get all users
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
):
    """Get list of all users"""
    service = UserService(db)
    users = await service.get_all_users()
    return users


# Get one user
@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get one user by id"""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return user


# Change user data
@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update user information"""
    service = UserService(db)
    updated_user = await service.update_user(user_id, user_data)
    return updated_user


# Remove user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete user from system"""
    service = UserService(db)
    await service.delete_user(user_id)
