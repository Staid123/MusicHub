from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserOut
from auth.utils import hash_password
from auth.custom_exceptions import (
    UserCreateException,
)
from database.models import Album, User


class AbstractRepository(ABC):
    @staticmethod
    @abstractmethod
    async def create_user():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def get_user_by_email():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def get_all_users():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def delete_user_account():
        raise NotImplementedError


class UserRepository(AbstractRepository):
    @staticmethod
    async def create_user(
        session: AsyncSession,
        username: str,
        email: str,
        password_hash: str
    ) -> int:
        try:
            new_user: User = User(
                username=username,
                email=email,
                password_hash=hash_password(password_hash)
            )
            session.add(new_user)
            await session.commit()
            return new_user.id
        except Exception:
            raise UserCreateException()
        
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email==email)
            .options(selectinload(User.albums).selectinload(Album.songs))
        )
        user: User = await session.scalars(stmt)
        return user.one_or_none()
    
    
    @staticmethod
    async def get_all_users(
        session: AsyncSession,
        skip: int,
        limit: int,
        user_id: int | None = None
    ) -> list[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.albums).selectinload(Album.songs)
            )
            .offset(skip)
            .limit(limit)
            .order_by(User.id)
        )

        if user_id is not None:
            stmt = stmt.filter_by(id=user_id)
        
        users = await session.scalars(stmt)
        return users.all()


    @staticmethod
    async def delete_user_account(
        session: AsyncSession,
        user: UserOut
    ) -> None:
        user_to_delete: User = await session.get(User, user.id)
        try:
            await session.delete(user_to_delete)
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not delete user"
            )

    @staticmethod
    async def change_user_role(
        session: AsyncSession,
        user_in: UserOut,
    ) -> User:
        user: User = await session.get(User, user_in.id)
        setattr(user, "role", user_in.role)
        await session.commit()
        
# Зависимость для получения репозитория 
def get_user_repository() -> UserRepository:
    return UserRepository