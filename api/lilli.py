import time
from fastapi import APIRouter
from models.api import AIRequest, AIResponse
from utils.logger import get_logger
from core.orchestrator import orchestrator

logger = get_logger(__name__)
start_time = time.time()

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "uptime": time.time() - start_time}

@router.post("/process_request", response_model=AIResponse)
async def process_request(request: AIRequest):
    try:
        logger.info(f"Processing request: {request.input}")

        result = await orchestrator.orchestrate(request.input)

        return AIResponse(
            output=result["response"],
            agent_name=result["delegated_agent"],
            error=", ".join(result["error"]) if result["error"] else ""
        )
    except Exception as e:
        logger.error(e)
        raise
