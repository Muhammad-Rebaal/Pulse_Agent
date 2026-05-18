from api.models.schemas import AnalysisRequest, InsightOutput, ImpactOutput

HIGH_URGENCY_TERMS = {
    "crisis", "default", "layoff", "recession", "war", "sanction", "shortage",
    "surge", "crash", "emergency", "bankruptcy", "volatile",
}

MEDIUM_URGENCY_TERMS = {
    "inflation", "rate", "raised", "increase", "decline", "drop", "slowdown",
    "tariff", "fuel", "oil", "debt", "loss",
}

PROFILE_IMPACTS = {
    "freelancer": {
        "high": "Client pipelines may shrink quickly, payment cycles can stretch, and income may become lumpier over the next few weeks.",
        "medium": "New work may still arrive, but pricing pressure and slower approvals could affect monthly cash flow.",
        "low": "The direct effect is limited for now, but it is worth watching client budget sentiment.",
    },
    "trader": {
        "high": "Expect sharp price swings, higher stop-out risk, and fast changes in market narrative.",
        "medium": "Portfolio risk is elevated; position sizing and sector exposure need review before the next trading session.",
        "low": "The signal is tradable mainly as a watchlist update unless volume or price confirms it.",
    },
    "sme": {
        "high": "Working capital, supplier pricing, and customer demand could be pressured within the next 30 days.",
        "medium": "Margins may tighten unless pricing, inventory, and vendor terms are adjusted early.",
        "low": "The effect is indirect, but it may still influence planning and procurement decisions.",
    },
    "salaried": {
        "high": "Household budget resilience and job security should be reviewed because income risk or cost pressure may rise.",
        "medium": "Monthly expenses and debt payments may need adjustment if prices or rates continue moving.",
        "low": "No immediate action is required, but savings and large purchases should be reviewed calmly.",
    },
}


def run_impact_agent(request: AnalysisRequest, insight: InsightOutput) -> ImpactOutput:
    text = f"{request.content} {insight.key_insight}".lower()
    high_hits = [term for term in HIGH_URGENCY_TERMS if term in text]
    medium_hits = [term for term in MEDIUM_URGENCY_TERMS if term in text]

    if high_hits or insight.relevance_score >= 9:
        urgency = "high"
    elif medium_hits or insight.relevance_score >= 7:
        urgency = "medium"
    else:
        urgency = "low"

    impact = PROFILE_IMPACTS[request.user_profile][urgency]
    triggers = high_hits[:3] or medium_hits[:3]
    if triggers:
        impact = f"{impact} Triggers detected: {', '.join(triggers)}."

    return ImpactOutput(financial_impact=impact, urgency=urgency)
