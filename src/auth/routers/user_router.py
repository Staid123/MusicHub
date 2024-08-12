import logging

from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from database import db_helper
from auth.service import UserService, get_user_service
from auth.schemas import UserOut


from auth.validation import (
    get_current_token_payload,
    get_current_active_auth_user,
    get_current_active_auth_user_admin
)


# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)

router = APIRouter(
    prefix="/users", 
    tags=["User Operations"],
)


@router.get(
    "/me/", 
    summary="Get user info",
)
async def auth_user_check_self_info(
    payload: Annotated[dict, Depends(get_current_token_payload)],
    user: Annotated[UserOut, Depends(get_current_active_auth_user)]
):
    iat = payload.get("iat")
    return {
        **user.model_dump(exclude_defaults=True),
        "logged_in_at": iat,
    }


@router.get(
    "/all/", 
    response_model=list[UserOut],
    summary="Get all users info"
)
async def get_list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    admin: Annotated[UserOut, Depends(get_current_active_auth_user_admin)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1),
    user_id: int | None = Query(default=None, gt=0)
) -> list[UserOut]:
    if admin:
        return await user_service.list_users(
            session=session,
            skip=skip,
            limit=limit,
            user_id=user_id
        )
    

@router.delete(
    "/delete/account/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account"
)
async def delete_user_account(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[UserOut, Depends(get_current_active_auth_user)],
) -> None:
    return await user_service.delete_user_account(
        session=session,
        user=user
    )