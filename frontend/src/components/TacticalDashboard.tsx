"use client";

import React from "react";
import { RecommendationResponse } from "@/types/coach";
import { PrimaryDirectiveCard } from "@/components/PrimaryDirectiveCard";
import { MilitaryPlanCard } from "@/components/MilitaryPlanCard";
import { EconomicBalanceCard } from "@/components/EconomicBalanceCard";
import { TimingStanceCard } from "@/components/TimingStanceCard";
import { ActionChecklistCard } from "@/components/ActionChecklistCard";
import { CombatSimulatorWidget } from "@/components/CombatSimulatorWidget";

interface TacticalDashboardProps {
  data: RecommendationResponse;
}

export const TacticalDashboard: React.FC<TacticalDashboardProps> = ({ data }) => {
  return (
    <div className="space-y-5 animate-in fade-in slide-in-from-bottom-3 duration-300">
      {/* 1. Primary Directive & Executive Summary */}
      <PrimaryDirectiveCard data={data} />

      {/* 2. Dual Action Plans: Military Response & Macro Economy */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <MilitaryPlanCard data={data} />
        <EconomicBalanceCard data={data} />
      </div>

      {/* 3. Dual Tactical Context: Stance Timing & Interactive Checklist */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <TimingStanceCard data={data} />
        <ActionChecklistCard data={data} />
      </div>

      {/* 4. Live Combat Duel Simulator Widget */}
      <CombatSimulatorWidget />
    </div>
  );
};
