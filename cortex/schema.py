from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RevenueMetrics(BaseModel):
    amount: Optional[float] = None
    frequency: str = "monthly"
    currency: str = "USD"

class KnowledgeNode(BaseModel):
    node_id: str
    video_id: str
    founder_name: str = ""
    startup_name: str = ""
    tech_stack: List[str] = []
    revenue_amount: Optional[float] = None
    revenue_frequency: str = "monthly"
    revenue_currency: str = "USD"
    key_lessons: List[str] = []
    timestamp: str = ""
    has_conflict: bool = False
    conflict_with_node_id: Optional[str] = None
    created_at: str = datetime.now().isoformat()
