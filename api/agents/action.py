from api.models.schemas import Action, ActionOutput, AnalysisRequest, ImpactOutput

ACTION_LIBRARY = {
    "freelancer": {
        "high": [
            ("Protect Cash Runway", "Pause non-essential spending and target a 60-90 day expense buffer before taking new risk."),
            ("Refill Client Pipeline", "Contact previous clients and pitch a small, fast-turnaround offer to reduce income gaps."),
            ("Tighten Payment Terms", "Ask for milestone payments or partial upfront deposits on new work."),
        ],
        "medium": [
            ("Diversify Client Base", "Reach out to prospects in two industries less exposed to the current signal."),
            ("Review Pricing", "Check whether new projects need a small buffer for currency, platform, or cost changes."),
            ("Create Backup Offer", "Package a lower-scope service that clients can approve faster."),
        ],
        "low": [
            ("Monitor Client Demand", "Track replies, proposal acceptance, and delayed invoices for two weeks."),
            ("Update Savings Target", "Add a small weekly buffer while the signal develops."),
        ],
    },
    "trader": {
        "high": [
            ("Reduce Position Size", "Cut exposure on high-volatility names until the market confirms direction."),
            ("Hedge Key Holdings", "Use protective puts or inverse exposure where liquidity and spreads are acceptable."),
            ("Set Hard Stops", "Define exits before entry and avoid averaging down during headline volatility."),
        ],
        "medium": [
            ("Review Sector Exposure", "Identify which holdings benefit or suffer from the detected macro signal."),
            ("Tighten Stop Losses", "Move stops closer on positions that have broken support or volume trends."),
            ("Wait For Confirmation", "Require price and volume confirmation before increasing risk."),
        ],
        "low": [
            ("Add To Watchlist", "Track related tickers and wait for volume confirmation."),
            ("Journal Thesis", "Write the trade thesis and invalidation level before acting."),
        ],
    },
    "sme": {
        "high": [
            ("Preserve Working Capital", "Delay discretionary purchases and protect payroll, inventory, and supplier payments."),
            ("Renegotiate Vendor Terms", "Ask key suppliers for longer payment windows or bulk-price protection."),
            ("Update Pricing Quickly", "Model whether prices need revision before margins compress further."),
        ],
        "medium": [
            ("Audit Input Costs", "Review top five costs and find which ones are most exposed to this news."),
            ("Adjust Inventory Plan", "Avoid overstocking slow-moving items while protecting critical inventory."),
            ("Improve Receivables", "Follow up overdue invoices and offer faster-payment incentives."),
        ],
        "low": [
            ("Monitor Margins", "Check gross margin weekly until the signal becomes clearer."),
            ("Prepare Supplier Backup", "Identify one alternate supplier for critical inputs."),
        ],
    },
    "salaried": {
        "high": [
            ("Strengthen Emergency Fund", "Prioritize cash savings until essential expenses are covered for three to six months."),
            ("Pause Major Purchases", "Delay large commitments until income and expense risk is clearer."),
            ("Reduce Variable Costs", "Cut flexible spending categories before fixed bills become stressful."),
        ],
        "medium": [
            ("Review Monthly Budget", "Update rent, food, transport, and debt assumptions based on the current signal."),
            ("Check Debt Exposure", "Prioritize expensive variable-rate debt if rates or inflation are rising."),
            ("Protect Income Options", "Refresh your CV and identify one practical secondary income path."),
        ],
        "low": [
            ("Track Household Prices", "Watch recurring bills and adjust savings goals if costs keep moving."),
            ("Review Savings Split", "Keep upcoming large expenses separate from emergency savings."),
        ],
    },
}


def run_action_agent(request: AnalysisRequest, impact: ImpactOutput) -> ActionOutput:
    action_rows = ACTION_LIBRARY[request.user_profile][impact.urgency]
    actions = [
        Action(title=title, description=description, simulate_available=index < 2)
        for index, (title, description) in enumerate(action_rows)
    ]
    return ActionOutput(actions=actions)
