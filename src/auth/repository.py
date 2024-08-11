from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
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
    def get_user_by_email():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    def get_all_users():
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
            .filter_by(id=user_id)
            .options(selectinload(User.albums).selectinload(Album.songs))
            .offset(skip)
            .limit(limit)
            .order_by(User.id)
        )
        users: list[User] = await session.scalars(stmt)
        return users.all()


# Зависимость для получения репозитория 
def get_user_repository() -> UserRepository:
    return UserRepository