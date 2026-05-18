from fastapi import APIRouter, HTTPException

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

PROFILE_BASELINES = {
    "freelancer": {
        "cash_reserves": "45 days",
        "income_stability": "Uneven",
        "risk_exposure": "Client concentration",
    },
    "trader": {
        "cash_reserves": "$2,000",
        "income_stability": "Market-dependent",
        "risk_exposure": "Elevated volatility",
    },
    "sme": {
        "cash_reserves": "1 payroll cycle",
        "income_stability": "Demand-sensitive",
        "risk_exposure": "Margin compression",
    },
    "salaried": {
        "cash_reserves": "1-2 months",
        "income_stability": "Moderate",
        "risk_exposure": "Inflation and debt costs",
    },
}

ACTION_EFFECTS = {
    "cash": ("cash_reserves", "Improved buffer"),
    "runway": ("cash_reserves", "Improved buffer"),
    "client": ("income_stability", "Broader pipeline"),
    "pipeline": ("income_stability", "Broader pipeline"),
    "payment": ("cash_reserves", "Faster collections"),
    "position": ("risk_exposure", "Reduced market exposure"),
    "hedge": ("risk_exposure", "Hedged downside"),
    "stop": ("risk_exposure", "Defined loss limit"),
    "vendor": ("cash_reserves", "Longer payment window"),
    "pricing": ("income_stability", "Protected margin"),
    "inventory": ("risk_exposure", "Lower stock risk"),
    "budget": ("cash_reserves", "More monthly surplus"),
    "debt": ("risk_exposure", "Lower rate pressure"),
    "emergency": ("cash_reserves", "Stronger safety net"),
}


@router.post("/simulate", response_model=SimulationResult)
async def simulate_action(request: SimulationRequest):
    before_state = PROFILE_BASELINES.get(request.user_profile, PROFILE_BASELINES["salaried"]).copy()
    after_state = before_state.copy()
    action_key = request.action_title.lower()

    changed = False
    for keyword, (field, value) in ACTION_EFFECTS.items():
        if keyword in action_key:
            after_state[field] = value
            changed = True

    if not changed:
        after_state["risk_exposure"] = "More actively managed"

    after_state["action_taken"] = request.action_title
    after_state["next_review"] = "7 days"

    profile_label = request.user_profile.replace("_", " ")
    return SimulationResult(
        whatsapp_draft=(
            f"Hi, quick update from PulseAgent: for your {profile_label} profile, "
            f"the recommended next move is '{request.action_title}'. Start with one small step today, "
            "track the result for a week, and only scale it if your cash flow and risk both improve."
        ),
        before_state=before_state,
        after_state=after_state,
    )
