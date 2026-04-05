from pydantic import BaseModel
from enum import Enum

class Priority(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"

class Category(str, Enum):
    BILLING = "billing"
    SUPPORT = "support"
    SPAM = "spam"
    INQUIRY = "inquiry"

class Email(BaseModel):
    id: str
    subject: str
    body: str
    from_email: str
    sender: str
    timestamp: str

class Label(BaseModel):
    priority: Priority
    category: Category

class TriageResult(BaseModel):
    email_id: str | None = None
    priority: Priority | None = None
    category: Category | None = None
    reply: str | None = None
    reasoning: str | None = None
