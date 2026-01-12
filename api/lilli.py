import time
from fastapi import APIRouter
from models.api import AIRequest, AIResponse
from utils.logger import get_logger

logger = get_logger(__name__)
start_time = time.time()

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "uptime": time.time() - start_time}

@router.post("/response", response_model=AIResponse)
async def get_ai_response(request: AIRequest):
    try:
        res = AIResponse(output="This is from this I guess")
        return res
    except Exception as e:
        logger.error(e)
        raise