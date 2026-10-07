from typing import Literal, Optional
from pydantic import BaseModel

class ActionItem(BaseModel):
    task: str
    owner: Optional[str] = None
    due_text: Optional[str] = None
    evidence_quote: str
    confidence: Literal["high", "medium", "low"] = "medium"

class Extraction(BaseModel):
    decisions: list[str] = []
    action_items: list[ActionItem] = []
    open_questions: list[str] = []
