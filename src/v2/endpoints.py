"""Module to define API routes for items."""

from fastapi import APIRouter

from logging_setup import setup_logger

logger = setup_logger()

router = APIRouter()

@router.get("/api_version_test/")
async def read_items():
    """Test Endpoint for API v2.

    Returns:
        list: The API current version.
    """
    logger.info("Fetching version")
    return [{"version": "v2"}]
