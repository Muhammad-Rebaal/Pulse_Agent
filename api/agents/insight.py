from api.models.schemas import AnalysisRequest, IngestOutput, InsightOutput

PROFILE_LENSES = {
    "freelancer": {
        "focus": "client budgets, project demand, cash runway, and currency/payment timing",
        "terms": {"layoff", "budget", "hiring", "startup", "software", "demand", "inflation"},
    },
    "trader": {
        "focus": "volatility, liquidity, rates, sentiment, and sector rotation",
        "terms": {"stock", "shares", "market", "rate", "inflation", "oil", "crypto", "earnings"},
    },
    "sme": {
        "focus": "input costs, customer demand, supplier terms, and working capital",
        "terms": {"cost", "supply", "demand", "tax", "fuel", "import", "loan", "inflation"},
    },
    "salaried": {
        "focus": "job stability, household costs, savings rate, and purchasing power",
        "terms": {"salary", "job", "layoff", "inflation", "rent", "loan", "rate", "consumer"},
    },
}

RISK_TERMS = {
    "surge", "rise", "raised", "increase", "inflation", "slowdown", "recession",
    "layoff", "cuts", "shortage", "volatile", "risk", "crisis", "default", "debt",
    "tariff", "sanction", "war", "conflict", "loss", "decline", "drop",
}

OPPORTUNITY_TERMS = {
    "growth", "expansion", "lower", "cut", "relief", "subsidy", "profit",
    "record", "demand", "hiring", "investment", "exports", "recovery",
}


def run_insight_agent(request: AnalysisRequest, ingest: IngestOutput) -> InsightOutput:
    lens = PROFILE_LENSES[request.user_profile]
    source_text = f"{request.content} {ingest.summary}".lower()
    profile_hits = sorted(term for term in lens["terms"] if term in source_text)
    risk_hits = sorted(term for term in RISK_TERMS if term in source_text)
    opportunity_hits = sorted(term for term in OPPORTUNITY_TERMS if term in source_text)

    score = 4 + min(3, len(profile_hits)) + min(2, len(risk_hits)) + min(1, len(opportunity_hits))
    relevance_score = max(1, min(10, score))

    if risk_hits and opportunity_hits:
        direction = "mixed risk and opportunity"
    elif risk_hits:
        direction = "risk-heavy"
    elif opportunity_hits:
        direction = "opportunity-led"
    else:
        direction = "watchlist-level"

    signal = ", ".join((profile_hits or risk_hits or opportunity_hits or ingest.entities)[:4])
    key_insight = (
        f"This looks like a {direction} signal for a {request.user_profile}. "
        f"The strongest connection is to {lens['focus']}. "
        f"Main detected signals: {signal}."
    )

    return InsightOutput(key_insight=key_insight, relevance_score=relevance_score)
