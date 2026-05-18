"use client";

import { useEffect, useRef, useState } from "react";

type AgentStep = {
  step_name: string;
  duration_ms: number;
  decision: string;
};

type AnalysisResult = {
  run_id: string;
  timestamp: string;
  steps: AgentStep[];
  ingest?: {
    summary: string;
    entities: string[];
  };
  insight?: {
    key_insight: string;
    relevance_score: number;
  };
  impact?: {
    financial_impact: string;
    urgency: "low" | "medium" | "high";
  };
  actions?: {
    actions: {
      title: string;
      description: string;
      simulate_available: boolean;
    }[];
  };
};

type SimulationState = {
  whatsapp_draft: string;
  before_state: Record<string, string>;
  after_state: Record<string, string>;
};

export default function Home() {
  const [content, setContent] = useState("");
  const [profile, setProfile] = useState("freelancer");
  const [contentType, setContentType] = useState<"text" | "url">("text");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  
  const [simulationState, setSimulationState] = useState<SimulationState | null>(null);
  const [simulationError, setSimulationError] = useState("");
  const [simulating, setSimulating] = useState(false);
  const simulationRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (simulationState) {
      simulationRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [simulationState]);

  const handleAnalyze = async () => {
    if (!content) return;
    setLoading(true);
    setResult(null);
    setSimulationState(null);
    setError("");

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content,
          content_type: contentType,
          user_profile: profile,
        }),
      });
      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail || "Backend analysis failed");
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async (actionTitle: string) => {
    setSimulating(true);
    setSimulationError("");
    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action_title: actionTitle,
          user_profile: profile,
        }),
      });
      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail || "Simulation failed");
      }
      const data = await res.json();
      setSimulationState(data);
    } catch (e) {
      setSimulationError(e instanceof Error ? e.message : "Simulation failed");
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-8 font-sans selection:bg-indigo-500/30">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            PulseAgent
          </h1>
          <p className="text-slate-400">Local multi-agent financial signal analyzer</p>
        </div>

        {/* Input Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl shadow-black/50 space-y-6">
          <div className="space-y-4">
            <div className="grid md:grid-cols-[180px_1fr] gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Content Type</label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value as "text" | "url")}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none"
                >
                  <option value="text">Text</option>
                  <option value="url">URL</option>
                </select>
              </div>
              <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Paste News or Content</label>
              <textarea 
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-32 bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300 placeholder:text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                placeholder={contentType === "url" ? "https://example.com/news-story" : "E.g., The central bank has unexpectedly raised interest rates by 50 basis points..."}
              />
              </div>
            </div>
            
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <label className="block text-sm font-medium text-slate-300 mb-2">Target Profile</label>
                <select 
                  value={profile}
                  onChange={(e) => setProfile(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none"
                >
                  <option value="freelancer">Freelancer</option>
                  <option value="trader">Day Trader</option>
                  <option value="sme">Small Business Owner</option>
                  <option value="salaried">Salaried Employee</option>
                </select>
              </div>
              <button 
                onClick={handleAnalyze}
                disabled={loading || !content}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white px-8 py-3 rounded-xl font-medium transition-all duration-200 active:scale-95"
              >
                {loading ? "Agents analyzing..." : "Run Financial Pipeline"}
              </button>
            </div>
            {error && (
              <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            
            {/* Agent Trace Log */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <h3 className="text-sm font-mono text-indigo-400 uppercase tracking-wider">Analysis Execution Trace</h3>
                <div className="text-xs font-mono text-slate-500">
                  {new Date(result.timestamp).toLocaleString()} · {String(result.run_id).slice(0, 8)}
                </div>
              </div>
              <div className="space-y-3">
                {result.steps.map((step, idx) => (
                  <div key={idx} className="flex items-center gap-4 text-sm font-mono bg-slate-950 p-3 rounded-lg border border-slate-800/50">
                    <span className="text-emerald-400">[{step.duration_ms}ms]</span>
                    <span className="text-cyan-300 font-bold w-32">{step.step_name}</span>
                    <span className="text-slate-400 truncate">{step.decision}</span>
                  </div>
                ))}
              </div>
            </div>

            {result.ingest && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <div className="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-2">Source Summary</div>
                <p className="text-slate-300 leading-relaxed mb-4">{result.ingest.summary}</p>
                <div className="flex flex-wrap gap-2">
                  {result.ingest.entities.map((entity: string) => (
                    <span key={entity} className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300">
                      {entity}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-6">
              {/* Insight & Impact */}
              <div className="space-y-6">
                {result.insight && (
                  <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-3xl rounded-full"></div>
                    <div className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2">Key Insight</div>
                    <p className="text-lg text-slate-200 leading-relaxed">{result.insight.key_insight}</p>
                    <div className="mt-4 inline-flex items-center gap-2 bg-indigo-500/10 text-indigo-300 px-3 py-1 rounded-full text-xs font-medium border border-indigo-500/20">
                      Relevance: {result.insight.relevance_score}/10
                    </div>
                  </div>
                )}
                
                {result.impact && (
                  <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <div className="text-xs font-bold text-rose-400 uppercase tracking-widest mb-2">Financial Impact</div>
                    <p className="text-slate-300 mb-4">{result.impact.financial_impact}</p>
                    <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                      result.impact.urgency === 'high' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                      result.impact.urgency === 'medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    }`}>
                      {result.impact.urgency} Urgency
                    </span>
                  </div>
                )}
              </div>

              {/* Actions */}
              {result.actions && (
                <div className="space-y-4">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">Recommended Actions</div>
                  {result.actions.actions.map((action, i) => (
                    <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/50 transition-colors group">
                      <h4 className="text-white font-medium mb-1 group-hover:text-indigo-400 transition-colors">{action.title}</h4>
                      <p className="text-sm text-slate-400 mb-4">{action.description}</p>
                      
                      {action.simulate_available && (
                        <button 
                          onClick={() => handleSimulate(action.title)}
                          disabled={simulating}
                          className="w-full bg-slate-950 border border-indigo-500/30 hover:border-indigo-500/80 text-indigo-300 py-2 rounded-lg text-sm font-medium transition-all"
                        >
                          {simulating ? "Simulating..." : "Simulate Impact"}
                        </button>
                      )}
                    </div>
                  ))}
                  {simulationError && (
                    <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">
                      {simulationError}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Simulation Results */}
            {simulationState && (
              <div ref={simulationRef} className="mt-12 bg-slate-900 border border-emerald-500/30 rounded-2xl p-8 shadow-[0_0_40px_-15px_rgba(16,185,129,0.2)] animate-in slide-in-from-bottom-8 duration-700">
                <h3 className="text-xl font-bold text-emerald-400 mb-8 flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
                  Simulation Result
                </h3>
                
                <div className="grid md:grid-cols-2 gap-8 mb-8">
                  <div className="space-y-3">
                    <div className="text-sm font-medium text-slate-500 uppercase">Before Strategy</div>
                    <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 font-mono text-sm space-y-2">
                      {Object.entries(simulationState.before_state).map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <span className="text-slate-500">{k}:</span>
                          <span className="text-slate-300">{v as string}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="text-sm font-medium text-emerald-500 uppercase">After Strategy</div>
                    <div className="bg-emerald-950/20 rounded-xl p-4 border border-emerald-500/30 font-mono text-sm space-y-2">
                      {Object.entries(simulationState.after_state).map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <span className="text-emerald-500/70">{k}:</span>
                          <span className="text-emerald-400">{v as string}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="text-sm font-medium text-slate-500 uppercase">WhatsApp AI Draft</div>
                  <div className="bg-[#0b141a] text-[#e9edef] p-4 rounded-xl rounded-tl-none inline-block max-w-[80%] relative shadow-lg">
                    {simulationState.whatsapp_draft}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
