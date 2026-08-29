"use client";

import React, { useState, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import {
  getAssetDatabase,
  getUnitImageUrl,
  AssetDatabase,
} from "@/lib/assetDb";
import { RefreshCw, Info, TrendingUp, TrendingDown, Clock, CheckSquare, Square } from "lucide-react";

interface TacticalSidebarProps {
  className?: string;
  isMobile?: boolean;
}

export const TacticalSidebar: React.FC<TacticalSidebarProps> = ({
  className = "",
  isMobile = false,
}) => {
  const {
    snapshot,
    recommendation,
    isLoading,
    getTacticalRecommendation,
    completedChecklistItems,
    toggleChecklistItem,
  } = useCoachStore();

  const [db, setDb] = useState<AssetDatabase>({});
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  useEffect(() => {
    getAssetDatabase().then(setDb);
  }, []);

  // Strategy & Advice
  const strategyTitle =
    recommendation?.tactical_stance?.recommended_stance ||
    recommendation?.primary_directive ||
    "FAST IMPERIAL BOOM";

  const strategyExplanation =
    recommendation?.explanation?.explanation?.coach_summary ||
    recommendation?.primary_directive ||
    `Exploit your ${snapshot.player_civ} power spike in Castle Age. Sighted enemy forces are vulnerable to ranged counters. Execute your gatherer rebalance now to support continuous military production and strike within the next timing window.`;

  // Military Focus Units
  const primaryUnit =
    recommendation?.counter_matrix?.primary_unit_recommendation ||
    recommendation?.military_action_plan?.primary_composition ||
    "Crossbowman";

  const secondaryUnit =
    recommendation?.counter_matrix?.secondary_support_unit ||
    recommendation?.military_action_plan?.secondary_composition ||
    "Scorpion";

  const militaryTooltip =
    recommendation?.explanation?.explanation?.military_plan?.counter_explanation ||
    recommendation?.counter_matrix?.tactical_summary ||
    `Identified enemy forces centered around ${snapshot.opponent_civ}. Recommended response: Mass ${primaryUnit} supported by ${secondaryUnit}. Focus fire on enemy siege and key high-value units.`;

  const primaryUnitImg = getUnitImageUrl(db, primaryUnit, snapshot.player_civ);
  const secondaryUnitImg = getUnitImageUrl(db, secondaryUnit, snapshot.player_civ);

  // Win Probability
  const winProbRaw = recommendation?.win_probability?.win_probability ?? 0.52;
  const winProbPercent = Math.round(winProbRaw * 100);
  const winAdvantage =
    recommendation?.win_probability?.advantage_level ||
    (winProbPercent >= 55 ? "favorable" : winProbPercent <= 45 ? "disadvantage" : "even match");

  // Action Timing
  const actionTiming =
    recommendation?.explanation?.explanation?.timing_plan?.attack_window ||
    recommendation?.tactical_stance?.urgency ||
    "Next 3 minutes";

  const actionTimingSubtitle =
    recommendation?.explanation?.explanation?.timing_plan?.threat_alert ||
    recommendation?.explanation?.explanation?.timing_plan?.strategic_spike_reasoning ||
    recommendation?.tactical_stance?.threat_alert ||
    `Enemy ${snapshot.opponent_civ} power spike incoming, strike now.`;

  // Eco Health & Villager Shifts
  const ecoGrade =
    recommendation?.economic_rebalance?.macro_health_grade || "C";

  const shifts = recommendation?.economic_rebalance?.villager_shifts || {
    food: 3,
    wood: -3,
    gold: 1,
    stone: -1,
  };

  const ecoTooltip =
    recommendation?.explanation?.explanation?.economic_plan?.macro_tip ||
    "Balance your eco to produce army continuously from all military buildings without floating excess stockpiles.";

  // Command Checklist
  const defaultChecklist = [
    `Produce ${primaryUnit} from military buildings`,
    `Add ${Math.abs(shifts.food || 3)} more villagers to Food`,
    "Research Scale Mail Armor / Blacksmith upgrades",
  ];

  const checklistItems =
    recommendation?.explanation?.explanation?.priority_checklist &&
    recommendation.explanation.explanation.priority_checklist.length > 0
      ? recommendation.explanation.explanation.priority_checklist
      : recommendation?.actionable_checklist &&
        recommendation.actionable_checklist.length > 0
      ? recommendation.actionable_checklist
      : defaultChecklist;

  const confidenceScore = recommendation
    ? Math.round(
        (recommendation.tactical_stance?.confidence ??
          recommendation.military_action_plan?.confidence ??
          0.78) * 100
      )
    : 78;

  return (
    <aside
      className={`${
        isMobile
          ? "w-full flex flex-col gap-4 py-2"
          : "hidden md:flex w-72 lg:w-80 fixed left-0 top-0 h-full bg-parchment-deep border-r border-outline-variant shadow-md flex-col py-6 px-4 z-40 overflow-y-auto"
      } ${className}`}
    >
      {/* Brand & Recalculate Button */}
      <div className="mb-4">
        <button
          type="button"
          onClick={() => getTacticalRecommendation()}
          disabled={isLoading}
          className="w-full bg-charcoal-ink text-on-primary font-label-tactical text-sm font-bold uppercase py-3 px-4 border border-gold-leaf hover:bg-blood-accent hover:border-gold-leaf transition-colors duration-200 shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-gold-leaf" />
              <span>CALCULATING...</span>
            </>
          ) : (
            <span>RECALCULATE</span>
          )}
        </button>
        <div className="mt-2 text-center font-headline-md text-xs text-on-surface-variant tracking-wider uppercase opacity-75">
          Confidence Score: {confidenceScore}%
        </div>
      </div>

      {/* Tactical Metrics Panels */}
      <div className="flex-1 flex flex-col gap-3.5">
        {/* 1. Current Strategy */}
        <div className="bg-surface parchment-panel border border-outline-variant rounded p-3.5 shadow-sm relative group">
          <div className="text-[11px] font-label-tactical text-on-surface-variant mb-1 uppercase tracking-widest font-bold">
            Current Strategy
          </div>
          <div className="font-headline-md text-primary leading-tight text-lg mb-1.5 font-bold">
            {strategyTitle}
          </div>
          <div className="font-body-md text-xs text-on-surface-variant leading-relaxed">
            {strategyExplanation}
          </div>
        </div>

        {/* 2. Military Focus */}
        <div className="bg-surface parchment-panel border border-outline-variant rounded p-3.5 shadow-sm relative group">
          <div className="absolute right-2 top-2">
            <button
              type="button"
              className="text-outline-variant hover:text-gold-leaf transition-colors"
              title={militaryTooltip}
              onClick={() =>
                setActiveTooltip(activeTooltip === "military" ? null : "military")
              }
            >
              <Info className="w-4 h-4" />
            </button>
          </div>
          <div className="text-[11px] font-label-tactical text-on-surface-variant mb-2 uppercase tracking-widest font-bold">
            Military Focus
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2.5 text-primary">
              {primaryUnitImg ? (
                <img
                  src={primaryUnitImg}
                  alt={primaryUnit}
                  className="w-6 h-6 object-contain rounded-sm border border-outline-variant bg-surface-variant"
                />
              ) : (
                <span className="material-symbols-outlined text-lg">sports_martial_arts</span>
              )}
              <span className="font-label-tactical font-bold text-sm">
                {primaryUnit}
              </span>
            </div>

            {secondaryUnit && (
              <div className="flex items-center gap-2.5 text-on-surface-variant">
                {secondaryUnitImg ? (
                  <img
                    src={secondaryUnitImg}
                    alt={secondaryUnit}
                    className="w-6 h-6 object-contain rounded-sm border border-outline-variant bg-surface-variant"
                  />
                ) : (
                  <span className="material-symbols-outlined text-lg">precision_manufacturing</span>
                )}
                <span className="font-label-tactical text-sm">
                  {secondaryUnit}
                </span>
              </div>
            )}
          </div>

          {activeTooltip === "military" && (
            <div className="mt-2.5 p-2 bg-surface-variant border border-outline-variant rounded text-[11px] font-body-md text-on-surface-variant leading-tight">
              {militaryTooltip}
            </div>
          )}
        </div>

        {/* 3. Win Probability */}
        <div className="bg-surface parchment-panel border border-outline-variant rounded p-3.5 shadow-sm relative overflow-hidden group">
          <div className="absolute right-0 top-0 w-10 h-full bg-surface-variant flex items-center justify-center border-l border-outline-variant opacity-70 group-hover:bg-gold-leaf group-hover:text-on-primary transition-colors">
            {winProbPercent >= 50 ? (
              <TrendingUp className="w-5 h-5 text-gold-leaf group-hover:text-on-primary" />
            ) : (
              <TrendingDown className="w-5 h-5 text-secondary group-hover:text-on-primary" />
            )}
          </div>
          <div className="text-[11px] font-label-tactical text-on-surface-variant mb-1 uppercase tracking-widest font-bold">
            Win Probability
          </div>
          <div className="font-headline-lg text-2xl font-bold text-primary leading-tight">
            {winProbPercent}%{" "}
            <span className="text-xs font-body-md text-on-surface-variant font-normal">
              ({winAdvantage})
            </span>
          </div>
        </div>

        {/* 4. Action Timing */}
        <div className="bg-surface parchment-panel border border-outline-variant rounded p-3.5 shadow-sm relative overflow-hidden group">
          <div className="absolute right-0 top-0 w-10 h-full bg-surface-variant flex items-center justify-center border-l border-outline-variant opacity-70 group-hover:bg-gold-leaf group-hover:text-on-primary transition-colors">
            <Clock className="w-5 h-5 text-gold-leaf group-hover:text-on-primary" />
          </div>
          <div className="text-[11px] font-label-tactical text-on-surface-variant mb-1 uppercase tracking-widest font-bold">
            Action Timing
          </div>
          <div className="font-label-tactical text-primary font-bold pr-8 leading-snug text-sm">
            {actionTiming}
            <div className="text-[10px] font-body-md text-secondary mt-1 font-normal leading-tight">
              {actionTimingSubtitle}
            </div>
          </div>
        </div>

        {/* 5. Eco Health */}
        <div className="bg-surface parchment-panel border border-outline-variant rounded p-3.5 shadow-sm relative group">
          <div className="absolute right-2 top-2">
            <button
              type="button"
              className="text-outline-variant hover:text-gold-leaf transition-colors"
              title={ecoTooltip}
              onClick={() => setActiveTooltip(activeTooltip === "eco" ? null : "eco")}
            >
              <Info className="w-4 h-4" />
            </button>
          </div>
          <div className="text-[11px] font-label-tactical text-on-surface-variant mb-2 uppercase tracking-widest font-bold">
            Eco Health
          </div>
          <div className="flex items-center gap-3">
            <div className="text-4xl font-headline-lg font-bold text-secondary">
              {ecoGrade}
            </div>
            <div className="grid grid-cols-2 gap-1 flex-1">
              <div
                className={`text-[10px] font-label-tactical px-1.5 py-0.5 rounded font-bold ${
                  (shifts.food ?? 0) >= 0
                    ? "text-tertiary bg-surface-variant"
                    : "text-secondary bg-surface-variant"
                }`}
              >
                F {(shifts.food ?? 0) >= 0 ? `+${shifts.food ?? 0}` : shifts.food}
              </div>
              <div
                className={`text-[10px] font-label-tactical px-1.5 py-0.5 rounded font-bold ${
                  (shifts.wood ?? 0) >= 0
                    ? "text-tertiary bg-surface-variant"
                    : "text-secondary bg-surface-variant"
                }`}
              >
                W {(shifts.wood ?? 0) >= 0 ? `+${shifts.wood ?? 0}` : shifts.wood}
              </div>
              <div
                className={`text-[10px] font-label-tactical px-1.5 py-0.5 rounded font-bold ${
                  (shifts.gold ?? 0) >= 0
                    ? "text-tertiary bg-surface-variant"
                    : "text-secondary bg-surface-variant"
                }`}
              >
                G {(shifts.gold ?? 0) >= 0 ? `+${shifts.gold ?? 0}` : shifts.gold}
              </div>
              <div
                className={`text-[10px] font-label-tactical px-1.5 py-0.5 rounded font-bold ${
                  (shifts.stone ?? 0) >= 0
                    ? "text-tertiary bg-surface-variant"
                    : "text-secondary bg-surface-variant"
                }`}
              >
                S {(shifts.stone ?? 0) >= 0 ? `+${shifts.stone ?? 0}` : shifts.stone}
              </div>
            </div>
          </div>
          {activeTooltip === "eco" && (
            <div className="mt-2.5 p-2 bg-surface-variant border border-outline-variant rounded text-[11px] font-body-md text-on-surface-variant leading-tight">
              {ecoTooltip}
            </div>
          )}
        </div>

        {/* 6. Command Checklist */}
        <div className="bg-surface parchment-panel border border-outline-variant rounded p-3.5 shadow-sm">
          <div className="text-[11px] font-label-tactical text-on-surface-variant mb-2 uppercase tracking-widest font-bold">
            Command Checklist
          </div>
          <ul className="space-y-2">
            {checklistItems.map((item, idx) => {
              const isChecked = !!completedChecklistItems[item];
              return (
                <li
                  key={idx}
                  onClick={() => toggleChecklistItem(item)}
                  className="flex items-start gap-2 text-xs font-body-md text-on-surface cursor-pointer select-none hover:text-primary transition-colors"
                >
                  <span className="mt-0.5 shrink-0 text-gold-leaf">
                    {isChecked ? (
                      <CheckSquare className="w-3.5 h-3.5 text-tertiary" />
                    ) : (
                      <Square className="w-3.5 h-3.5 text-outline" />
                    )}
                  </span>
                  <span className={isChecked ? "line-through opacity-60" : ""}>
                    {item}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </aside>
  );
};
