"use client";

import React from "react";
import { RecommendationResponse } from "@/types/coach";
import { Wheat, Trees, Coins, Mountain, ArrowRight, RefreshCw, AlertCircle } from "lucide-react";

interface EconomicBalanceCardProps {
  data: RecommendationResponse;
}

export const EconomicBalanceCard: React.FC<EconomicBalanceCardProps> = ({ data }) => {
  const eco = data.economic_rebalance || {};
  const expEco = data.explanation?.explanation?.economic_plan || {
    problem_diagnosis: "Economy distribution is stable.",
    immediate_action: "Maintain steady production.",
    target_villager_allocation: {},
    macro_tip: "Queue villagers continuously without TC idle time.",
  };

  const current = eco.current_allocation || { food: 0, wood: 0, gold: 0, stone: 0 };
  const target = expEco.target_villager_allocation || eco.target_allocation || { food: 0, wood: 0, gold: 0, stone: 0 };

  const getDeltaBadge = (res: "food" | "wood" | "gold" | "stone") => {
    const curVal = current[res] ?? 0;
    const tgtVal = target[res] ?? curVal;
    const diff = tgtVal - curVal;
    if (diff === 0) return <span className="text-slate-400 font-mono text-xs">Balanced</span>;
    if (diff > 0)
      return (
        <span className="text-emerald-400 font-mono text-xs font-bold bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-900/40">
          +{diff} Vills
        </span>
      );
    return (
      <span className="text-rose-400 font-mono text-xs font-bold bg-rose-950/60 px-1.5 py-0.5 rounded border border-rose-900/40">
        {diff} Vills
      </span>
    );
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30">
              <Wheat className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
              Economic Rebalancing & Solver
            </h3>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
            {eco.production_sustainability_status || (eco.macro_health_grade ? `Grade ${eco.macro_health_grade}` : "Optimized")}
          </span>
        </div>

        {/* Macro Diagnosis & Immediate Move */}
        <div className="mb-4 space-y-2.5">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
            <div className="flex items-center gap-1.5 text-amber-400 font-semibold mb-1">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Macro Bottleneck Diagnosis:</span>
            </div>
            <p className="text-slate-300">
              {expEco.problem_diagnosis ||
                eco.identified_economic_bottlenecks?.join("; ") ||
                eco.floating_stockpile_warnings?.join("; ") ||
                "Stockpiles are steady."}
            </p>
          </div>

          <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-300 font-bold mb-1">
              <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
              <span>Immediate Villager Reallocation:</span>
            </div>
            <p className="text-emerald-100 font-medium">
              {expEco.immediate_action ||
                eco.actionable_rebalance_order ||
                eco.shift_instructions?.join("; ") ||
                eco.summary ||
                "Rebalance villagers toward target army production."}
            </p>
          </div>
        </div>

        {/* Current vs Target Villagers Comparison Table */}
        <div className="mb-4">
          <span className="text-xs font-semibold text-slate-300 block mb-2">
            Villager Distribution Target:
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {/* Food */}
            <div className="bg-slate-950 border border-red-950 rounded-lg p-2.5 text-center">
              <span className="flex items-center justify-center gap-1 text-[11px] font-bold text-red-400 mb-1">
                <Wheat className="w-3.5 h-3.5" /> Food
              </span>
              <div className="flex items-center justify-center gap-1 text-xs font-mono font-semibold text-slate-300 mb-1">
                <span>{current.food ?? 0}</span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
                <span className="text-amber-300 font-bold text-sm">{target.food ?? current.food ?? 0}</span>
              </div>
              <div>{getDeltaBadge("food")}</div>
            </div>

            {/* Wood */}
            <div className="bg-slate-950 border border-amber-950 rounded-lg p-2.5 text-center">
              <span className="flex items-center justify-center gap-1 text-[11px] font-bold text-amber-400 mb-1">
                <Trees className="w-3.5 h-3.5" /> Wood
              </span>
              <div className="flex items-center justify-center gap-1 text-xs font-mono font-semibold text-slate-300 mb-1">
                <span>{current.wood ?? 0}</span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
                <span className="text-amber-300 font-bold text-sm">{target.wood ?? current.wood ?? 0}</span>
              </div>
              <div>{getDeltaBadge("wood")}</div>
            </div>

            {/* Gold */}
            <div className="bg-slate-950 border border-yellow-950 rounded-lg p-2.5 text-center">
              <span className="flex items-center justify-center gap-1 text-[11px] font-bold text-yellow-400 mb-1">
                <Coins className="w-3.5 h-3.5" /> Gold
              </span>
              <div className="flex items-center justify-center gap-1 text-xs font-mono font-semibold text-slate-300 mb-1">
                <span>{current.gold ?? 0}</span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
                <span className="text-amber-300 font-bold text-sm">{target.gold ?? current.gold ?? 0}</span>
              </div>
              <div>{getDeltaBadge("gold")}</div>
            </div>

            {/* Stone */}
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-center">
              <span className="flex items-center justify-center gap-1 text-[11px] font-bold text-slate-300 mb-1">
                <Mountain className="w-3.5 h-3.5" /> Stone
              </span>
              <div className="flex items-center justify-center gap-1 text-xs font-mono font-semibold text-slate-300 mb-1">
                <span>{current.stone ?? 0}</span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
                <span className="text-amber-300 font-bold text-sm">{target.stone ?? current.stone ?? 0}</span>
              </div>
              <div>{getDeltaBadge("stone")}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Macro Coaching Tip */}
      {expEco.macro_tip && (
        <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 italic">
          💡 {expEco.macro_tip}
        </div>
      )}
    </div>
  );
};
