from pydantic import BaseModel


class SiteSettingCreate(BaseModel):
    key: str
    value: str
    description: str | None = None
    is_public: bool = True


class SiteSettingUpdate(BaseModel):
    value: str | None = None
    description: str | None = None
    is_public: bool | None = None


class SiteSettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: str | None = None
    is_public: bool

    class Config:
        from_attributes = True