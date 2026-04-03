import uuid
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.request_exception import DuplicateEntityError, NotFoundError
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service to manage users in database"""

    def __init__(self, db: AsyncSession):
        # db: connection to database
        self.db = db

    async def _check_company_name_exists(
        self, company_name: str, exclude_user_id: uuid.UUID | None = None
    ) -> bool:
        """Check if company name already used in database"""
        # Find user with this company name
        query = select(UserModel).where(UserModel.company_name == company_name)

        # If we are updating, ignore the current user , myself, because I can keep the same company name
        if exclude_user_id:
            query = query.where(UserModel.id != exclude_user_id)

        # Return True if company name exists
        return bool(await self.db.scalar(query))

    async def create_user(self, user_schema: UserCreate) -> UserModel:
        """Add new user to database"""
        # Check that company name is not used before
        if await self._check_company_name_exists(user_schema.company_name):
            raise DuplicateEntityError(
                message="This company name already in use",
                details={"field": "company_name", "value": user_schema.company_name},
            )

        # Create new user object
        new_user = UserModel(**user_schema.model_dump())
        self.db.add(new_user)

        try:
            # Save to database
            await self.db.commit()
            # Refresh to get generated values (like id)
            await self.db.refresh(new_user)
            return new_user

        except SQLAlchemyError:
            # If error, undo changes
            await self.db.rollback()
            raise

    async def get_all_users(self) -> list[UserModel]:
        """Get all users from database"""
        # TODO: add lazy load for projects, to not load all projects with users
        result: Result[UserModel] = await self.db.scalars(select(UserModel))
        return result.all()

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserModel:
        """Find one user by id"""
        user = await self.db.get(UserModel, user_id)

        # If user does not exist, raise error
        if not user:
            raise NotFoundError("User not found")

        return user

    async def update_user(
        self, user_id: uuid.UUID, user_schema: UserUpdate
    ) -> UserModel:
        """Change user data. Only change fields that user provides"""
        # Find user
        user = await self.db.get(UserModel, user_id)

        # Check if user exists
        if not user:
            raise NotFoundError("User not found")

        # If user wants to change company name, check it is not used
        if user_schema.company_name and user_schema.company_name != user.company_name:
            if await self._check_company_name_exists(
                user_schema.company_name, exclude_user_id=user_id
            ):
                raise DuplicateEntityError("This company name already in use")

        # Change only the fields that user sent
        update_data = user_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        try:
            # Save changes to database
            await self.db.commit()
            # Refresh to get new values
            await self.db.refresh(user)
            return user

        except SQLAlchemyError:
            # If error, undo changes
            await self.db.rollback()
            raise

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Remove user from database"""
        # Find user
        user = await self.db.get(UserModel, user_id)

        # Check if user exists
        if not user:
            raise NotFoundError("User not found")

        # Remove user
        await self.db.delete(user)

        try:
            # Save the delete
            await self.db.commit()
        except SQLAlchemyError:
            # If error, undo delete
            await self.db.rollback()
            raise
