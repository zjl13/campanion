from pydantic import BaseModel


class BuddyCreateRequest(BaseModel):
    style: str
    tone: str = "supportive"
    strictness: str
    buddy_type: str
    language: str = "zh-CN"


class BuddyResponse(BaseModel):
    buddy_id: str
    display_name: str
    persona_summary: str

