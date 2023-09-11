"""Module to define API routes for items."""

from fastapi import APIRouter

from src.logging_setup import setup_logger

logger = setup_logger()

router = APIRouter()

@router.get("/items/")
async def read_items():
    """Test Endpoint for API v2 to read items.

    Returns:
        list: A list of items.
    """
    logger.info("Fetching items")
    return [{"name": "Bar"}]
