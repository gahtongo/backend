from fastapi import APIRouter, HTTPException, status
from app.services.ai_triage_service import extract_report_from_chat

from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIContentOptimizeRequest,
    AIContentOptimizeResponse,
)
from app.services.ai_triage_service import generate_support_reply, optimize_content

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIChatResponse)
def chat_with_ai(payload: AIChatRequest):
    try:
        return generate_support_reply(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI assistant is unavailable right now: {str(exc)}",
        ) from exc


@router.post("/optimize-content", response_model=AIContentOptimizeResponse)
def optimize_content_with_ai(payload: AIContentOptimizeRequest):
    try:
        return optimize_content(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI optimizer is unavailable right now: {str(exc)}",
        ) from exc


@router.post("/extract-report")
def extract_report(payload: AIChatRequest):
    try:
        return extract_report_from_chat(payload.messages)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))