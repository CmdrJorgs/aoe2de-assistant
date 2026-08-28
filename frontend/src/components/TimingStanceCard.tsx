"use client";

import React from "react";
import { RecommendationResponse } from "@/types/coach";
import { Timer, AlertTriangle, Flame, Compass } from "lucide-react";

interface TimingStanceCardProps {
  data: RecommendationResponse;
}

export const TimingStanceCard: React.FC<TimingStanceCardProps> = ({ data }) => {
  const stance = data.tactical_stance || {};
  const timing = data.explanation?.explanation?.timing_plan || {
    posture: "FORWARD PRESSURE",
    attack_window: "Active Window (Next 3–5 min)",
    strategic_spike_reasoning: "Maintain map control and pressure opponent.",
    threat_alert: null,
  };

  const stanceName =
    stance.recommended_stance ||
    stance.stance_class ||
    timing.posture ||
    "FORWARD_PRESSURE";

  const isAggressive =
    Boolean(stance.is_attack_window_active) ||
    stanceName.toLowerCase().includes("aggression") ||
    stanceName.toLowerCase().includes("pressure") ||
    stance.urgency === "HIGH" ||
    stance.urgency === "CRITICAL";

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg border ${isAggressive ? "bg-red-500/20 text-red-400 border-red-500/30" : "bg-cyan-500/20 text-cyan-400 border-cyan-500/30"}`}>
              {isAggressive ? <Flame className="w-4 h-4" /> : <Compass className="w-4 h-4" />}
            </div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
              Strategic Stance & Timing
            </h3>
          </div>
          <span
            className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
              isAggressive
                ? "bg-red-950/60 border-red-800/80 text-red-300 animate-pulse"
                : "bg-cyan-950/60 border-cyan-800/80 text-cyan-300"
            }`}
          >
            {timing.posture || stanceName.replace(/_/g, " ").toUpperCase()}
          </span>
        </div>

        {/* Attack Window Banner */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
              <Timer className="w-3.5 h-3.5 text-amber-400" />
              <span>Optimal Attack Timing:</span>
            </span>
            <span className="text-xs font-bold text-amber-300 font-mono">
              {timing.attack_window || (stance.attack_window_sec ? `Next ${Math.round(stance.attack_window_sec / 60)} min` : "Active Window (Next 3–5 min)")}
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1.5 border-t border-slate-900">
            {timing.strategic_spike_reasoning || stance.summary || stance.tactical_directive || "Coordinate army production before pushing."}
          </p>
        </div>

        {/* Threat Alert / Power Spike Warning */}
        {(timing.threat_alert || stance.threat_spike_alert || stance.threat_alert) && (
          <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-900/40 text-xs">
            <div className="flex items-center gap-1.5 text-amber-400 font-bold mb-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Opponent Danger Window Alert:</span>
            </div>
            <p className="text-amber-200/90 leading-relaxed">
              {timing.threat_alert || stance.threat_spike_alert || stance.threat_alert}
            </p>
          </div>
        )}
      </div>

      {/* Civ Power Spike Source */}
      <div className="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
        <span>Power Spike Source:</span>
        <span className="text-slate-200 font-medium font-mono">
          {stance.civ_power_spike || stance.power_spike_source || "Standard Tech Curve"}
        </span>
      </div>
    </div>
  );
};
