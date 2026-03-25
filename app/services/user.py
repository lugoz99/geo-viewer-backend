import uuid
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.request_exception import DuplicateEntityError, NotFoundError
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _check_company_name_exists(
        self, company_name: str, exclude_user_id: uuid.UUID | None = None
    ) -> bool:
        """Genérico: verifica si company_name ya existe (excluyendo un user si se especifica)"""
        query = select(UserModel).where(UserModel.company_name == company_name)

        if exclude_user_id:
            query = query.where(UserModel.id != exclude_user_id)

        result = await self.db.scalar(query)
        return result is not None

    async def create_user(self, user_schema: UserCreate) -> UserModel:
        # Validar ANTES que company_name no exista
        if await self._check_company_name_exists(user_schema.company_name):
            raise DuplicateEntityError("The company name already exists")

        new_user = UserModel(**user_schema.model_dump())
        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user

        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_all_users(self) -> list[UserModel]:
        result: Result[UserModel] = await self.db.scalars(select(UserModel))
        return result.all()

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserModel:
        user = await self.db.get(UserModel, user_id)

        if not user:
            raise NotFoundError("User not found")

        return user

    async def update_user(
        self, user_id: uuid.UUID, user_schema: UserUpdate
    ) -> UserModel:
        """Actualizar usuario (solo campos proporcionados)"""
        user = await self.db.get(UserModel, user_id)

        if not user:
            raise NotFoundError("User not found")

        if user_schema.company_name and user_schema.company_name != user.company_name:
            if await self._check_company_name_exists(
                user_schema.company_name, exclude_user_id=user_id
            ):
                raise DuplicateEntityError("The company name already exists")

        # Actualizar solo los campos proporcionados
        update_data = user_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user

        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.db.get(UserModel, user_id)

        if not user:
            raise NotFoundError("User not found")

        await self.db.delete(user)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
