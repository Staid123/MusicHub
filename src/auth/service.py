from abc import ABC, abstractmethod
from auth.enums import Role
from database.models import User
from auth.repository import (
    UserRepository, 
    get_user_repository
)
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserIn, UserOut
from auth.custom_exceptions import UserCreateException
from music.service.album_service import AlbumService, get_album_service


class AbstractUserService(ABC):
    @staticmethod
    @abstractmethod
    async def register_user():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def get_user_by_email():
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    async def list_users():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def check_user_role():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def delete_user_account():
        raise NotImplementedError
    

class UserService(AbstractUserService):
    @staticmethod
    async def register_user(
        session: AsyncSession, 
        user_in: UserIn,
        user_repository: UserRepository = get_user_repository()
    ) -> int:
        try:
            new_user_id = await user_repository.create_user(
                session=session,
                **user_in.model_dump()
            )
            return new_user_id
        except UserCreateException as ex:
            return f"{ex}: failure to create new user"

    @staticmethod
    async def get_user_by_email(
        session: AsyncSession, 
        email: str,
        user_repository: UserRepository = get_user_repository(),
    ) -> UserOut:
        user: User = await user_repository.get_user_by_email(
            session=session, 
            email=email
        )
        if user:
            return UserOut.model_validate(obj=user, from_attributes=True)
        return None
    

    @staticmethod
    async def list_users(
        session: AsyncSession,
        skip: int,
        limit: int,
        user_id: int | None = None,
        user_repository: UserRepository = get_user_repository()
    ) -> list[UserOut]:
        users = await user_repository.get_all_users(
            session=session,
            skip=skip,
            limit=limit,
            user_id=user_id
        )
        users_schemas = [UserOut.model_validate(user, from_attributes=True) for user in users]
        return users_schemas
    

    @staticmethod
    async def check_user_role(
        user_in: UserIn,
        session: AsyncSession,
    ) -> str:
        user = await UserService.get_user_by_email(
            session=session, 
            email=user_in.email
        )
        return str(user.role)
    

    @staticmethod
    async def delete_user_account(
        session: AsyncSession,
        user: UserOut,
        user_repository: UserRepository = get_user_repository(),
        album_service: AlbumService = get_album_service()
    ) -> None:
        for album in user.albums:
            await album_service.delete_album(
                session=session, 
                album_id=album.id,
                user=user
            )
        await user_repository.delete_user_account(session=session, user=user)


# Зависимость для получения сервиса
def get_user_service() -> UserService:
    return UserService