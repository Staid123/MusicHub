import logging
from typing import Annotated

from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordBearer #, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from auth.enums import Role
from auth.utils import (
    validate_password,
    decode_jwt
)
from database import db_helper_test, db_helper
from auth.schemas import UserOut
from sqlalchemy.orm import Session
from auth.custom_exceptions import (
    unactive_user_exception,
    unauthed_user_exception,
    invalid_token_type_exception,
    token_not_found_exception,
    invalid_token_error,
    not_enough_rights_exception
)

from auth.actions import (
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
)

from auth.service import UserService, get_user_service

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)

# Use a logger for this module
logger = logging.getLogger(__name__)


# интерфейс для введения имени и пароля, а затем автоматическое получение токена и отправка его в заголовки
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/jwt/auth/login/",
)


# Проверка, что юзер зарегистрирован
async def validate_auth_user(
    session: Annotated[Session, Depends(db_helper.session_getter)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    username: str = Form(),
    password: str = Form(),
):
    # Get user by username
    if not (
        user := await user_service.get_user_by_email(
            session=session, email=username
        )
    ):
        raise unauthed_user_exception

    if not validate_password(
        password=password,
        hashed_password=user.password_hash,
    ):
        logger.warning(f"Login attempt failed. Incorrect password for user with email: '{username}'.")
        raise unauthed_user_exception

    if not user.active:
        raise unactive_user_exception
    logger.info(f"Login attempt with username: {user.username}")
    logger.info("USER ROLE: %s", user.role)
    return user


# Проверка типа токена
async def validate_token_type(
    payload: dict, 
    token_type: str
) -> bool:
    if payload.get(TOKEN_TYPE_FIELD) == token_type:
        return True
    raise invalid_token_type_exception


# Получение информации с токена 
def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    try:
        payload = decode_jwt(
            token=token,
        )
        logger.info("TOKEN %s", token)
    except InvalidTokenError:
        raise invalid_token_error
    return payload


# Получение пользователя по полю sub из токена
async def get_user_by_token_sub(
    payload: dict,
    user_service: UserService = get_user_service(),
) -> UserOut:
    email: str | None = payload.get("sub")
    if email is None:
        logger.warning("Token payload does not contain 'sub'")
        raise token_not_found_exception

    user: UserOut = await user_service.get_user_by_email(
        # session=db_helper.session_factory(), 
        session=db_helper_test.session_factory(),
        email=email
    )
    
    if user and user.active:
        logger.info(f"User found by email: {email}")
        return user

    logger.warning(f"User not found or inactive: {email}")
    raise token_not_found_exception


# фабрика для создания функций (вводится тип токена, который ожидается)
def get_auth_user_from_token_of_type(token_type: str):
    # Функция для получения информации с токена 
    async def get_auth_user_from_token(
        # получаем токен с заголовков
        payload: Annotated[dict, Depends(get_current_token_payload)]
    ) -> UserOut:
        logger.debug(f"Validating token type: expected {token_type}, got {payload.get('type')}")
        # проверяем, совпадает ли введенный токен с токеном в заголовке
        await validate_token_type(payload=payload, token_type=token_type)
        # получаем данные по токену
        return await get_user_by_token_sub(payload)
    return get_auth_user_from_token


# Проверка, что юзер аутентифицирован для выпуска access token'a
get_current_auth_user = get_auth_user_from_token_of_type(token_type=ACCESS_TOKEN_TYPE)
# Проверка, что юзер аутентифицирован для выпуска refresh token'a
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type(token_type=REFRESH_TOKEN_TYPE)


# Проверка, что юзер аутентифицирован + активен
def get_current_active_auth_user(
    user: Annotated[UserOut, Depends(get_current_auth_user)]
) -> UserOut:
    if user.active:
        return user
    raise unactive_user_exception


# Проверка, что юзер является админом
def get_current_active_auth_user_admin(
    user: Annotated[UserOut, Depends(get_current_active_auth_user)]
) -> UserOut:
    result: bool = user.role == Role.ADMIN
    if result:
        return user
    raise not_enough_rights_exception