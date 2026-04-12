from pydantic import BaseModel, Field


class AIChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class AIChatRequest(BaseModel):
    messages: list[AIChatMessage] = Field(min_length=1)
    mode: str = Field(default="support", max_length=50)


class AIChatResponse(BaseModel):
    reply: str
    suggested_actions: list[str] = Field(default_factory=list)
    risk_level: str = "normal"


class AIContentOptimizeRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    headline: str | None = Field(default=None, max_length=255)
    excerpt: str | None = None
    content: str = Field(min_length=20)
    category: str | None = Field(default=None, max_length=100)


class AIContentOptimizeResponse(BaseModel):
    headline: str
    excerpt: str
    ticker: str
    category_hint: str | None = None