"use client";

import React from "react";
import { RecommendationResponse } from "@/types/coach";
import { Zap, TrendingUp, ShieldCheck, Bot } from "lucide-react";

interface PrimaryDirectiveCardProps {
  data: RecommendationResponse;
}

export const PrimaryDirectiveCard: React.FC<PrimaryDirectiveCardProps> = ({ data }) => {
  const winProb = data.win_probability;
  const explanation = data.explanation?.explanation;
  const isFallback = data.explanation?.was_fallback;

  // Advantage color
  const winP = winProb?.win_probability ?? 0.5;
  const winPctStr =
    winProb?.win_probability_percent || `${Math.round(winP * 100)}%`;
  const isFavorable = winP >= 0.55;
  const isCritical = winP < 0.4;

  const stanceText = (
    data.tactical_stance?.recommended_stance ||
    data.tactical_stance?.stance_class ||
    explanation?.timing_plan?.posture ||
    "FORWARD PRESSURE"
  )
    .replace(/_/g, " ")
    .toUpperCase();

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30 border border-amber-500/40 rounded-2xl p-5 shadow-2xl gold-glow relative overflow-hidden">
      {/* Background ambient accent */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Badges */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b border-amber-500/20">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-[11px] font-bold tracking-wider uppercase px-2.5 py-1 rounded-md bg-amber-500 text-slate-950 font-mono shadow-sm">
            <Zap className="w-3.5 h-3.5 fill-current" />
            Tactical Directive
          </span>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300 font-mono">
            {data.match_context.player_civ} vs {data.match_context.opponent_civ} ({data.match_context.formatted_time})
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* ELO Calibration Badge */}
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-950 border border-amber-500/40 text-amber-300">
            {explanation?.elo_tier ? `${explanation.elo_tier.toUpperCase()} TIER` : "CALIBRATED"}
          </span>

          {/* Verification Badge */}
          <div className="flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 px-2 py-0.5 rounded-full">
            <ShieldCheck className="w-3 h-3" />
            <span>{isFallback ? "Deterministic Verified" : "LLM + Tech Tree Verified"}</span>
          </div>
        </div>
      </div>

      {/* Primary Directive Headline */}
      <div className="mb-4">
        <h2 className="text-xl sm:text-2xl font-black text-amber-300 tracking-tight leading-snug">
          {data.primary_directive}
        </h2>
        <p className="mt-2 text-sm text-slate-200 leading-relaxed bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-xl">
          &ldquo;{explanation?.coach_summary || data.military_action_plan?.tactical_notes || "Execute tactical plan."}&rdquo;
        </p>
      </div>

      {/* Metrics Row: Win Probability & Urgency */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
        {/* Win Probability */}
        <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block">
              Win Probability
            </span>
            <div className="flex items-baseline gap-1.5 mt-0.5">
              <span className={`text-lg font-mono font-bold ${isFavorable ? "text-emerald-400" : isCritical ? "text-rose-400" : "text-amber-400"}`}>
                {winPctStr}
              </span>
              <span className="text-xs text-slate-400">({winProb?.advantage_level?.replace(/_/g, " ") || "Even"})</span>
            </div>
          </div>
          <div className={`p-2 rounded-lg ${isFavorable ? "bg-emerald-950/60 text-emerald-400" : "bg-amber-950/60 text-amber-400"}`}>
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        {/* Stance Posture */}
        <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block">
              Tactical Stance
            </span>
            <span className="text-sm font-bold text-slate-100 mt-0.5 block truncate">
              {stanceText}
            </span>
          </div>
          <div className="p-2 rounded-lg bg-amber-950/60 text-amber-400">
            <Zap className="w-5 h-5" />
          </div>
        </div>

        {/* Latency & Compute */}
        <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-3 flex items-center justify-between sm:col-span-2 md:col-span-1">
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block">
              Decision Latency
            </span>
            <span className="text-sm font-mono font-bold text-cyan-300 mt-0.5 block">
              {data.total_latency_ms} ms <span className="text-[10px] text-slate-400">({data.inference_latency_ms}ms ML)</span>
            </span>
          </div>
          <div className="p-2 rounded-lg bg-cyan-950/60 text-cyan-400">
            <Bot className="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>
  );
};
