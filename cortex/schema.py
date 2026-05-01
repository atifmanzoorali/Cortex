from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class KnowledgeNode(BaseModel):
    node_id: str
    video_id: str
    founder_name: Optional[str] = None
    startup_name: Optional[str] = None
    tech_stack: List[str] = []
    revenue_amount: Optional[float] = None
    revenue_frequency: Optional[str] = None
    revenue_currency: str = "USD"
    key_lessons: List[str] = []
    timestamp: Optional[str] = None
    has_conflict: bool = False
    conflict_with_node_id: Optional[str] = None
    created_at: str = datetime.now().isoformat()
