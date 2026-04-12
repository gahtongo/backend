from __future__ import annotations

from pydantic import BaseModel
from openai import OpenAI

from app.core.config import get_settings
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIContentOptimizeRequest,
    AIContentOptimizeResponse,
)

settings = get_settings()


def _get_client() -> OpenAI:
    if not settings.OPENAI_API_KEY.strip():
        raise ValueError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _build_history_transcript(messages: list) -> str:
    if not messages:
        return ""

    lines: list[str] = []

    for item in messages[-12:]:
        role = getattr(item, "role", None) or (
            item.get("role", "user") if isinstance(item, dict) else "user"
        )
        content = getattr(item, "content", None) or (
            item.get("content", "") if isinstance(item, dict) else ""
        )

        if not content:
            continue

        lines.append(f"{str(role).upper()}: {str(content).strip()}")

    return "\n".join(lines).strip()


def _infer_risk_level(user_message: str, ai_reply: str) -> str:
    combined = f"{user_message} {ai_reply}".lower()

    urgent_terms = [
        "immediate danger",
        "locked",
        "cannot leave",
        "being forced",
        "threat",
        "violence",
        "abuse",
        "trafficking",
        "unsafe",
        "help now",
        "kidnapped",
        "they will hurt me",
    ]

    medium_terms = [
        "scared",
        "afraid",
        "worried",
        "not safe",
        "control me",
        "coercion",
        "pressured",
        "manipulated",
    ]

    if any(term in combined for term in urgent_terms):
        return "high"

    if any(term in combined for term in medium_terms):
        return "elevated"

    return "normal"


def _suggest_actions(user_message: str, risk_level: str) -> list[str]:
    message = user_message.lower()

    if risk_level == "high":
        return [
            "Move to a safer place if you can do so without increasing your risk.",
            "Contact emergency support or a trusted person immediately.",
            "Use the report page if calling is not safe.",
        ]

    if "report" in message or "trafficking" in message:
        return [
            "Write down the most important facts you know.",
            "Submit a confidential report when safe.",
            "Contact GAHTO directly if urgent help is needed.",
        ]

    return [
        "Take the next safest step available to you.",
        "Use WhatsApp or call support if you need direct human help.",
    ]


def generate_support_reply(payload: AIChatRequest) -> AIChatResponse:
    client = _get_client()

    user_messages = [
        msg.content.strip()
        for msg in payload.messages
        if msg.role == "user"
    ]
    latest_user_message = user_messages[-1] if user_messages else ""

    if not latest_user_message:
        raise ValueError("A user message is required")

    history_text = _build_history_transcript(payload.messages[:-1])

    instructions = (
        "You are GAHTO's safety-focused support assistant for anti-human-trafficking help. "
        "Be calm, clear, compassionate, and practical. "
        "Prioritize immediate safety over long explanations. "
        "Do not shame the user. "
        "Do not give legal certainty or claim rescue is guaranteed. "
        "When risk seems urgent, tell the user to move to a safer place if possible, "
        "contact direct support, and use the report pathway if calling is unsafe. "
        "Keep responses concise, supportive, and action-oriented."
    )

    composed_input = (
        "Conversation history:\n"
        f"{history_text or 'No earlier history.'}\n\n"
        "Latest user message:\n"
        f"{latest_user_message}"
    )

    response = client.responses.create(
        model=getattr(settings, "AI_CHAT_MODEL", "gpt-5.4"),
        instructions=instructions,
        input=composed_input,
    )

    reply_text = (response.output_text or "").strip()

    if not reply_text:
        reply_text = (
            "I’m here with you. If you are in immediate danger, move to a safer "
            "place if possible and contact direct support right away."
        )

    risk_level = _infer_risk_level(latest_user_message, reply_text)
    suggested_actions = _suggest_actions(latest_user_message, risk_level)

    return AIChatResponse(
        reply=reply_text,
        suggested_actions=suggested_actions,
        risk_level=risk_level,
    )


def optimize_content(
    payload: AIContentOptimizeRequest,
) -> AIContentOptimizeResponse:
    client = _get_client()

    instructions = (
        "You improve NGO/public-interest content for clarity, trust, urgency, and readability. "
        "Return polished copy that is professional, human, and concise. "
        "Write in a credible NGO media tone. "
        "Do not invent facts not present in the source."
    )

    optimize_prompt = f"""
You are improving a GAHTO content item.

Title:
{payload.title}

Current headline:
{payload.headline or 'None'}

Current excerpt:
{payload.excerpt or 'None'}

Category:
{payload.category or 'general'}

Content:
{payload.content}

Return JSON-like plain text with four labeled sections:
HEADLINE:
EXCERPT:
TICKER:
CATEGORY_HINT:

Rules:
- HEADLINE max 110 characters
- EXCERPT max 220 characters
- TICKER max 72 characters
- CATEGORY_HINT should be a short recommendation such as: press-coverage, rescue-update, breaking, campaign, awareness, general
- Do not use markdown fences
""".strip()

    response = client.responses.create(
        model=getattr(settings, "AI_OPTIMIZER_MODEL", "gpt-5.4"),
        instructions=instructions,
        input=optimize_prompt,
    )

    raw = (response.output_text or "").strip()

    headline = payload.headline or payload.title
    excerpt = payload.excerpt or payload.content[:200].strip()
    ticker = (payload.headline or payload.title)[:72]
    category_hint = payload.category or "general"

    for line in raw.splitlines():
        normalized = line.strip()

        if normalized.upper().startswith("HEADLINE:"):
            headline = normalized.split(":", 1)[1].strip() or headline

        elif normalized.upper().startswith("EXCERPT:"):
            excerpt = normalized.split(":", 1)[1].strip() or excerpt

        elif normalized.upper().startswith("TICKER:"):
            ticker = normalized.split(":", 1)[1].strip() or ticker

        elif normalized.upper().startswith("CATEGORY_HINT:"):
            category_hint = (
                normalized.split(":", 1)[1].strip() or category_hint
            )

    return AIContentOptimizeResponse(
        headline=headline[:110].strip(),
        excerpt=excerpt[:220].strip(),
        ticker=ticker[:72].strip(),
        category_hint=category_hint[:100].strip() or None,
    )


class AIExtractedReport(BaseModel):
    case_type: str
    urgency: str
    description: str
    location: str | None = None
    incident_time: str | None = None
    additional_notes: str | None = None
    confidence: float


def extract_report_from_chat(messages: list) -> AIExtractedReport:
    client = _get_client()

    transcript = _build_history_transcript(messages)

    instructions = (
        "You extract structured incident reports from conversations related to human trafficking. "
        "Be accurate and conservative. Do NOT invent details. "
        "If information is missing, leave it empty."
    )

    prompt = f"""
Conversation:
{transcript}

Extract structured report fields.

Return plain text in this format:

CASE_TYPE:
URGENCY:
DESCRIPTION:
LOCATION:
INCIDENT_TIME:
ADDITIONAL_NOTES:
CONFIDENCE:

Rules:
- CASE_TYPE: short label (e.g. Suspected Trafficking)
- URGENCY: Low, Medium, or Urgent
- DESCRIPTION: concise but complete
- CONFIDENCE: number between 0 and 1
- Do not include markdown
""".strip()

    response = client.responses.create(
        model=getattr(settings, "AI_CHAT_MODEL", "gpt-5.4"),
        instructions=instructions,
        input=prompt,
    )

    raw = (response.output_text or "").strip()

    data = {
        "case_type": "Suspected Trafficking",
        "urgency": "Urgent",
        "description": "",
        "location": None,
        "incident_time": None,
        "additional_notes": None,
        "confidence": 0.5,
    }

    for line in raw.splitlines():
        line = line.strip()

        if line.upper().startswith("CASE_TYPE:"):
            data["case_type"] = (
                line.split(":", 1)[1].strip() or data["case_type"]
            )

        elif line.upper().startswith("URGENCY:"):
            data["urgency"] = (
                line.split(":", 1)[1].strip() or data["urgency"]
            )

        elif line.upper().startswith("DESCRIPTION:"):
            data["description"] = line.split(":", 1)[1].strip()

        elif line.upper().startswith("LOCATION:"):
            val = line.split(":", 1)[1].strip()
            data["location"] = val or None

        elif line.upper().startswith("INCIDENT_TIME:"):
            val = line.split(":", 1)[1].strip()
            data["incident_time"] = val or None

        elif line.upper().startswith("ADDITIONAL_NOTES:"):
            val = line.split(":", 1)[1].strip()
            data["additional_notes"] = val or None

        elif line.upper().startswith("CONFIDENCE:"):
            try:
                data["confidence"] = float(
                    line.split(":", 1)[1].strip()
                )
            except Exception:
                pass

    return AIExtractedReport(**data)