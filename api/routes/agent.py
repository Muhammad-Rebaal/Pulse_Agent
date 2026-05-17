from fastapi import APIRouter, HTTPException
from datetime import datetime
import time

from api.models.schemas import AnalysisRequest, AgentRunResult, SimulationRequest, SimulationResult
from api.services.antigravity import get_analysis_pipeline

router = APIRouter()

@router.post("/analyze", response_model=AgentRunResult)
async def analyze_content(request: AnalysisRequest):
    try:
        pipeline = get_analysis_pipeline()
        result = pipeline.run(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import asyncio

@router.post("/simulate", response_model=SimulationResult)
async def simulate_action(request: SimulationRequest):
    await asyncio.sleep(1) # Mock processing time
    
    # Make the mock dynamic so it changes based on what action was clicked!
    is_freelancer = request.user_profile == "freelancer"
    currency = "$" if not is_freelancer else "$"
    
    return SimulationResult(
        whatsapp_draft=f"Hi! Based on your {request.user_profile} profile, we noticed you decided to '{request.action_title}'. Here are the next steps to proceed with this strategy safely.",
        before_state={
            "cash_reserves": "Low" if is_freelancer else "$2,000", 
            "risk_exposure": "High"
        },
        after_state={
            "cash_reserves": "Stable" if is_freelancer else "$2,800", 
            "risk_exposure": "Optimized",
            "action_taken": request.action_title
        }
    )
