import time
from fastapi import APIRouter
from utils.logger import get_logger

logger = get_logger(__name__)
start_time = time.time()

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "uptime": time.time() - start_time}
