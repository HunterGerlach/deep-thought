from fastapi import APIRouter

from src.config import Config
from src.logging_setup import setup_logger

config = Config()
logger = setup_logger()

router = APIRouter()

@router.get("/items/")
async def read_items():
    return [{"name": "Bar"}]
