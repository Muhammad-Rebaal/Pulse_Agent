import time
import uuid
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

from api.models.schemas import (
    AnalysisRequest, AgentRunResult, AgentStep, 
    IngestOutput, InsightOutput, ImpactOutput, ActionOutput, Action
)

class AntigravityWorkflow:
    """Mock implementation of the Antigravity workflow API for the hackathon."""
    def __init__(self):
        self.nodes = []

    def add_node(self, name: str, handler):
        self.nodes.append({"name": name, "handler": handler})

    def run(self, request: AnalysisRequest) -> AgentRunResult:
        run_id = str(uuid.uuid4())
        current_input = None
        steps = []
        results = {}
        
        for node in self.nodes:
            start_time = time.time()
            node_name = node["name"]
            
            # Execute the node handler, passing the original request and the previous output
            output = node["handler"](request, current_input)
            
            duration_ms = int((time.time() - start_time) * 1000)
            decision = f"Processed data through {node_name} successfully."
            
            steps.append(AgentStep(
                step_name=node_name,
                duration_ms=duration_ms,
                decision=decision
            ))
            
            results[node_name] = output
            current_input = output # Pass output to next node

        return AgentRunResult(
            run_id=run_id,
            timestamp=datetime.now(),
            steps=steps,
            ingest=results.get("IngestAgent"),
            insight=results.get("InsightAgent"),
            impact=results.get("ImpactAgent"),
            actions=results.get("ActionAgent")
        )

# Define handlers for each agent with DYNAMIC logic based on profile and input
def run_ingest_agent(req: AnalysisRequest, prev_out: Any) -> IngestOutput:
    time.sleep(0.3)
    # Pick a few keywords from their text dynamically
    words = [w for w in req.content.split() if len(w) > 5][:3]
    return IngestOutput(
        summary=f"Ingested breaking {req.content_type} concerning: {' '.join(words)}...",
        entities=[w.capitalize() for w in words] if words else ["Market", "Economy"]
    )

def run_insight_agent(req: AnalysisRequest, ingest: IngestOutput) -> InsightOutput:
    time.sleep(0.4)
    insights = {
        "freelancer": "Demand for flexible gig work may shift as a result of this development.",
        "trader": "This event signals high likelihood of short-term price swings and volatility.",
        "sme": "Cost of goods and operational overhead may be directly affected.",
        "salaried": "Overall job market stability and purchasing power might be impacted."
    }
    return InsightOutput(
        key_insight=insights.get(req.user_profile, "General economic shifts expected."),
        relevance_score=9
    )

def run_impact_agent(req: AnalysisRequest, insight: InsightOutput) -> ImpactOutput:
    time.sleep(0.3)
    impacts = {
        "freelancer": ("Potential 15% drop in new freelance contracts this quarter.", "medium"),
        "trader": ("High risk of margin calls if heavily leveraged in affected sectors.", "high"),
        "sme": ("Cash flow could tighten significantly within the next 30-60 days.", "high"),
        "salaried": ("Inflationary pressure might reduce your discretionary income by 5%.", "low")
    }
    text, urgency = impacts.get(req.user_profile, ("Minor impact", "low"))
    return ImpactOutput(financial_impact=text, urgency=urgency)

def run_action_agent(req: AnalysisRequest, impact: ImpactOutput) -> ActionOutput:
    time.sleep(0.5)
    actions_map = {
        "freelancer": [
            Action(title="Diversify Client Base", description="Reach out to 5 new prospects outside your usual industry.", simulate_available=True),
            Action(title="Increase Cash Reserves", description="Delay large purchases to maintain a 3-month buffer.", simulate_available=False)
        ],
        "trader": [
            Action(title="Hedge Positions", description="Buy protective puts on your largest tech holdings.", simulate_available=True),
            Action(title="Tighten Stop Losses", description="Move stop losses to 3% below current support levels.", simulate_available=True)
        ],
        "sme": [
            Action(title="Delay Capital Expenditure", description="Hold off on new equipment purchases until Q4.", simulate_available=True),
            Action(title="Renegotiate Vendor Terms", description="Ask suppliers for net-60 terms instead of net-30.", simulate_available=False)
        ],
        "salaried": [
            Action(title="Review Emergency Fund", description="Ensure you have 6 months of living expenses saved.", simulate_available=True),
            Action(title="Delay Major Purchases", description="Hold off on buying a new car or house for now.", simulate_available=False)
        ]
    }
    return ActionOutput(actions=actions_map.get(req.user_profile, []))

# Configure the pipeline
def get_analysis_pipeline() -> AntigravityWorkflow:
    pipeline = AntigravityWorkflow()
    pipeline.add_node("IngestAgent", run_ingest_agent)
    pipeline.add_node("InsightAgent", run_insight_agent)
    pipeline.add_node("ImpactAgent", run_impact_agent)
    pipeline.add_node("ActionAgent", run_action_agent)
    return pipeline
