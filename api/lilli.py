from fastapi import APIRouter
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/api/health")
async def health_check():
    return {"status": "200"}
