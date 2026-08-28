"use client";

import React from "react";
import { RecommendationResponse } from "@/types/coach";
import { Swords, Hammer, Crosshair, ChevronRight, Lightbulb } from "lucide-react";

interface MilitaryPlanCardProps {
  data: RecommendationResponse;
}

export const MilitaryPlanCard: React.FC<MilitaryPlanCardProps> = ({ data }) => {
  const mil = data.military_action_plan || {};
  const expMil = data.explanation?.explanation?.military_plan || {
    primary_unit_recommendation: mil.primary_composition || "Knights",
    secondary_unit_recommendation: mil.secondary_composition || null,
    production_building_instruction: mil.recommended_building || "Stables",
    key_tech_priorities: mil.recommended_tech_order || [],
    counter_explanation: mil.strategic_summary || "Deploy counter composition against enemy forces.",
    micro_positioning_tip: null,
  };
  const counter = data.counter_matrix || {
    production_building_target: "Production Buildings",
    tactical_summary: "Counter matrix active.",
  };

  const techPriorities =
    expMil.key_tech_priorities?.length > 0
      ? expMil.key_tech_priorities
      : mil.recommended_tech_order || ["Scale Barding Armor", "Bloodlines"];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Swords className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
              Military Action Plan
            </h3>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-amber-400">
            {Math.round((mil.confidence || 0.8) * 100)}% Confidence
          </span>
        </div>

        {/* Primary Unit & Buildings Banner */}
        <div className="bg-slate-950 border border-amber-900/40 rounded-xl p-3.5 mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-slate-400 font-medium">Primary Unit Focus:</span>
            <span className="text-xs font-bold text-amber-300 font-mono">
              {expMil.primary_unit_recommendation || mil.primary_composition}
            </span>
          </div>
          {expMil.secondary_unit_recommendation && (
            <div className="flex items-center justify-between mb-1.5 text-xs">
              <span className="text-slate-400">Support Unit:</span>
              <span className="text-slate-200 font-medium">{expMil.secondary_unit_recommendation}</span>
            </div>
          )}
          <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-xs">
            <span className="text-slate-400">Production Buildings:</span>
            <span className="font-semibold text-cyan-300 font-mono">
              {expMil.production_building_instruction || counter.production_building_target}
            </span>
          </div>
        </div>

        {/* Key Upgrades & Tech Order */}
        <div className="mb-4">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
            <Hammer className="w-3.5 h-3.5 text-yellow-400" />
            <span>Blacksmith & Tech Priority Order:</span>
          </label>
          <div className="flex flex-wrap items-center gap-1.5">
            {techPriorities.map((tech, idx) => (
              <React.Fragment key={tech}>
                <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs font-medium text-amber-200">
                  <span className="text-amber-400 font-bold mr-1">{idx + 1}.</span> {tech}
                </span>
                {idx < techPriorities.length - 1 && (
                  <ChevronRight className="w-3 h-3 text-slate-600" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Counter Rationale */}
        <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl mb-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-300 font-semibold mb-1">
            <Crosshair className="w-3.5 h-3.5 text-rose-400" />
            <span>Combat Counter Matrix Reasoning:</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {expMil.counter_explanation || counter.tactical_summary}
          </p>
        </div>
      </div>

      {/* Micro / Tactical Positioning Tip */}
      {expMil.micro_positioning_tip && (
        <div className="pt-3 border-t border-slate-800/80 flex items-start gap-2 text-xs text-amber-300/90 bg-amber-950/20 p-2.5 rounded-lg border border-amber-900/30">
          <Lightbulb className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <span>
            <strong className="text-amber-300">Micro Tip:</strong> {expMil.micro_positioning_tip}
          </span>
        </div>
      )}
    </div>
  );
};
