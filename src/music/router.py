# Logger setup
import logging

from fastapi import APIRouter


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(message)s'
)

router = APIRouter(
    prefix="/music", 
    tags=["Music Operations"],
)


@router.get("/", response_model=)