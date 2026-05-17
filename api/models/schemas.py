from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

class AnalysisRequest(BaseModel):
    content: str = Field(..., description="The content to analyze")
    content_type: Literal["text", "url", "pdf"] = Field(..., description="The type of the content")
    user_profile: Literal["freelancer", "trader", "sme", "salaried"] = Field(..., description="The profile of the user")

class AgentStep(BaseModel):
    step_name: str
    duration_ms: int
    decision: str

class IngestOutput(BaseModel):
    summary: str = Field(..., description="Summary of the ingested content")
    entities: List[str] = Field(..., description="Key entities extracted")

class InsightOutput(BaseModel):
    key_insight: str = Field(..., description="The core insight derived from the content")
    relevance_score: int = Field(..., ge=1, le=10, description="Relevance score out of 10")

class ImpactOutput(BaseModel):
    financial_impact: str = Field(..., description="How this impacts the user financially")
    urgency: Literal["low", "medium", "high"] = Field(..., description="Urgency of the impact")

class Action(BaseModel):
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Action description")
    simulate_available: bool = Field(default=False, description="Whether this action can be simulated")

class ActionOutput(BaseModel):
    actions: List[Action] = Field(..., description="List of recommended actions")

class AgentRunResult(BaseModel):
    run_id: str
    timestamp: datetime
    steps: List[AgentStep]
    ingest: Optional[IngestOutput] = None
    insight: Optional[InsightOutput] = None
    impact: Optional[ImpactOutput] = None
    actions: Optional[ActionOutput] = None

class SimulationRequest(BaseModel):
    action_title: str
    user_profile: str

class SimulationResult(BaseModel):
    whatsapp_draft: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
