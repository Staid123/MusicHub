from fastapi import HTTPException, status
from jwt import InvalidTokenError


class UserCreateException(Exception):
    def init(self, message="Failed to create user"):
        self.message = message
        super().init(self.message)


unauthed_user_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid username or password",
)


unactive_user_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="user inactive",
)


token_not_found_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token invalid (user not found)",
)


invalid_token_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"invalid token error: {InvalidTokenError}",
)


invalid_token_type_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"invalid token type"
)


not_enough_rights_exception = HTTPException(
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    detail=f"have not enough rights"
)


user_already_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User with this email already exists"
)


user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)


update_ban_status_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to update user's ban status"
)