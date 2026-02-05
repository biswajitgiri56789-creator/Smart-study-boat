from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Question:
    id: Optional[int] = None
    class_key: str = ""
    subject_key: str = ""
    question: str = ""
    importance: str = "medium"
    marks: int = 5
    chapter: str = ""
    posted_count: int = 0
    last_posted: Optional[datetime] = None
    created_at: Optional[datetime] = None

@dataclass
class PostedHistory:
    id: Optional[int] = None
    question_id: int = 0
    post_date: datetime = None
    post_time: datetime = None