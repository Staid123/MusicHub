from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from auth.routers.auth_router import router as auth_router
from auth.routers.user_router import router as user_router

# интерфейс для введения токена (который автоматически отправляеятся в заголовки) после логина
http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/jwt", 
    # интерфейс для введения токена (который автоматически отправляеятся в заголовки) после логина
    dependencies=[Depends(http_bearer)]
)

router.include_router(auth_router)
router.include_router(user_router)