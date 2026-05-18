import time
import uuid
from typing import Any, Callable, TypedDict
from datetime import datetime

from api.models.schemas import (
    AnalysisRequest, AgentRunResult, AgentStep,
)
from api.agents.ingest import run_ingest_agent
from api.agents.insight import run_insight_agent
from api.agents.impact import run_impact_agent
from api.agents.action import run_action_agent

class WorkflowNode(TypedDict):
    name: str
    handler: Callable[[AnalysisRequest, Any], Any]


class AntigravityWorkflow:
    """Small local workflow runner that executes the financial analysis agents."""
    def __init__(self):
        self.nodes: list[WorkflowNode] = []

    def add_node(self, name: str, handler: Callable[[AnalysisRequest, Any], Any]):
        self.nodes.append({"name": name, "handler": handler})

    def run(self, request: AnalysisRequest) -> AgentRunResult:
        run_id = str(uuid.uuid4())
        current_input = None
        steps = []
        results = {}
        
        for node in self.nodes:
            start_time = time.time()
            node_name = node["name"]
            handler = node["handler"]

            output = handler(request, current_input)
            duration_ms = int((time.time() - start_time) * 1000)
            decision = _decision_for(node_name, output, duration_ms)
            
            steps.append(AgentStep(
                step_name=node_name,
                duration_ms=duration_ms,
                decision=decision
            ))
            
            results[node_name] = output
            current_input = output

        return AgentRunResult(
            run_id=run_id,
            timestamp=datetime.now(),
            steps=steps,
            ingest=results.get("IngestAgent"),
            insight=results.get("InsightAgent"),
            impact=results.get("ImpactAgent"),
            actions=results.get("ActionAgent")
        )

def _decision_for(node_name: str, output: Any, duration_ms: int) -> str:
    if node_name == "IngestAgent":
        return f"Extracted {len(output.entities)} signals and generated a source-grounded summary in {duration_ms}ms."
    if node_name == "InsightAgent":
        return f"Scored profile relevance at {output.relevance_score}/10 and identified the core financial signal."
    if node_name == "ImpactAgent":
        return f"Classified user urgency as {output.urgency} from detected financial risk terms."
    if node_name == "ActionAgent":
        return f"Generated {len(output.actions)} tailored actions; simulations enabled for priority actions."
    return f"Processed {node_name} in {duration_ms}ms."


def _ingest_node(request: AnalysisRequest, prev_out: Any):
    return run_ingest_agent(request)


def _insight_node(request: AnalysisRequest, prev_out: Any):
    return run_insight_agent(request, prev_out)


def _impact_node(request: AnalysisRequest, prev_out: Any):
    return run_impact_agent(request, prev_out)


def _action_node(request: AnalysisRequest, prev_out: Any):
    return run_action_agent(request, prev_out)

def get_analysis_pipeline() -> AntigravityWorkflow:
    pipeline = AntigravityWorkflow()
    pipeline.add_node("IngestAgent", _ingest_node)
    pipeline.add_node("InsightAgent", _insight_node)
    pipeline.add_node("ImpactAgent", _impact_node)
    pipeline.add_node("ActionAgent", _action_node)
    return pipeline
