"use client";

import React, { useState, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import { TacticalSidebar } from "@/components/TacticalSidebar";
import { Header } from "@/components/Header";
import { MatchSetup } from "@/components/MatchSetup";
import { EconomyInput } from "@/components/EconomyInput";
import { SightedEntitiesPicker } from "@/components/SightedEntitiesPicker";
import { VoiceInputModal } from "@/components/VoiceInputModal";
import { TrendingUp, Bolt, Clock, AlertCircle } from "lucide-react";

export default function Home() {
  const {
    recommendation,
    isLoading,
    error,
    getTacticalRecommendation,
    loadMetadata,
  } = useCoachStore();

  const [isVoiceOpen, setIsVoiceOpen] = useState<boolean>(false);
  const [activeNav, setActiveNav] = useState<string>("war-room");
  const [mobileTab, setMobileTab] = useState<"input" | "output">("input");

  useEffect(() => {
    loadMetadata();
  }, [loadMetadata]);

  // Initial calculation trigger if none loaded
  useEffect(() => {
    if (!recommendation && !isLoading) {
      getTacticalRecommendation();
    }
  }, [recommendation, isLoading, getTacticalRecommendation]);

  const winProbPercent = Math.round(
    (recommendation?.win_probability?.win_probability ?? 0.52) * 100
  );

  const strategyTitle =
    recommendation?.tactical_stance?.recommended_stance ||
    recommendation?.primary_directive ||
    "FAST IMPERIAL BOOM";

  const actionTiming =
    recommendation?.explanation?.explanation?.timing_plan?.attack_window ||
    recommendation?.tactical_stance?.urgency ||
    "Next 3 mins";

  return (
    <div className="min-h-screen bg-background text-on-background flex flex-col font-body-md selection:bg-gold-leaf selection:text-on-primary">
      {/* Left Side: Calculated Output (Tactical Sidebar on Desktop) */}
      <TacticalSidebar />

      {/* Right Side: Main Content & User Input Area */}
      <main className="md:ml-72 lg:ml-80 min-h-screen flex flex-col flex-1">
        {/* Top App Header */}
        <Header
          onOpenVoice={() => setIsVoiceOpen(true)}
          activeNav={activeNav}
          onSelectNav={setActiveNav}
        />

        {/* Canvas / Dashboard Content */}
        <div className="flex-1 p-4 sm:p-6 max-w-container-max mx-auto w-full space-y-6 pb-28 md:pb-8">
          {/* Error Banner */}
          {error && (
            <div className="p-4 rounded-lg bg-error-container border border-error text-error text-xs flex items-center gap-3 shadow-sm">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <div className="flex-1 font-medium">
                <strong>Error:</strong> {error}
              </div>
              <button
                type="button"
                onClick={() => getTacticalRecommendation()}
                className="px-3 py-1 bg-error text-on-error rounded font-label-tactical text-xs cursor-pointer"
              >
                Retry
              </button>
            </div>
          )}

          {/* Mobile Metrics Banner (Visible on Mobile) */}
          <div className="md:hidden grid grid-cols-1 sm:grid-cols-3 gap-3 mb-2">
            <div className="bg-surface parchment-panel p-3.5 rounded-lg shadow-sm border border-outline-variant flex justify-between items-center relative overflow-hidden">
              <div className="z-10">
                <div className="text-[10px] font-label-tactical text-on-surface-variant uppercase tracking-wider font-bold">
                  Win Probability
                </div>
                <div className="font-headline-md text-primary mt-0.5 text-lg font-bold">
                  {winProbPercent}%{" "}
                  <span className="text-xs font-body-md text-on-surface-variant font-normal">
                    (even)
                  </span>
                </div>
              </div>
              <TrendingUp className="w-8 h-8 text-gold-leaf opacity-30 absolute right-3" />
            </div>

            <div className="bg-surface parchment-panel p-3.5 rounded-lg shadow-sm border border-outline-variant flex justify-between items-center relative overflow-hidden">
              <div className="z-10">
                <div className="text-[10px] font-label-tactical text-on-surface-variant uppercase tracking-wider font-bold">
                  Tactical Stance
                </div>
                <div className="font-label-tactical text-primary font-bold mt-0.5 text-xs truncate max-w-[140px]">
                  {strategyTitle}
                </div>
              </div>
              <Bolt className="w-8 h-8 text-gold-leaf opacity-30 absolute right-3" />
            </div>

            <div className="bg-surface parchment-panel p-3.5 rounded-lg shadow-sm border border-outline-variant flex justify-between items-center relative overflow-hidden">
              <div className="z-10">
                <div className="text-[10px] font-label-tactical text-on-surface-variant uppercase tracking-wider font-bold">
                  Action Timing
                </div>
                <div className="font-label-tactical text-primary font-bold mt-0.5 text-xs">
                  {actionTiming}
                </div>
              </div>
              <Clock className="w-8 h-8 text-gold-leaf opacity-30 absolute right-3" />
            </div>
          </div>

          {/* Mobile Output Drawer Toggle (When mobile user wants to see full sidebar metrics) */}
          <div className="md:hidden flex gap-2 mb-2">
            <button
              type="button"
              onClick={() => setMobileTab("input")}
              className={`flex-1 py-2 rounded text-xs font-label-tactical font-bold border transition-colors ${
                mobileTab === "input"
                  ? "bg-gold-leaf text-on-primary border-gold-leaf shadow-sm"
                  : "bg-surface text-on-surface-variant border-outline-variant"
              }`}
            >
              Match Inputs
            </button>
            <button
              type="button"
              onClick={() => setMobileTab("output")}
              className={`flex-1 py-2 rounded text-xs font-label-tactical font-bold border transition-colors ${
                mobileTab === "output"
                  ? "bg-gold-leaf text-on-primary border-gold-leaf shadow-sm"
                  : "bg-surface text-on-surface-variant border-outline-variant"
              }`}
            >
              Calculated Output & Checklist
            </button>
          </div>

          {mobileTab === "output" ? (
            <div className="md:hidden">
              <TacticalSidebar isMobile={true} />
            </div>
          ) : (
            <>
              {/* 1. MATCH CONTEXT & SETUP */}
              <MatchSetup />

              {/* 2. LIVE ECONOMY & STOCKPILE */}
              <EconomyInput />

              {/* 3. FOG OF WAR: TACTICAL GRID */}
              <SightedEntitiesPicker />
            </>
          )}
        </div>
      </main>

      {/* Voice Input Modal */}
      <VoiceInputModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
      />

      {/* Bottom Nav Bar (Mobile Only) */}
      <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 bg-parchment-deep border-t border-outline-variant shadow-2xl md:hidden">
        <button
          type="button"
          onClick={() => setMobileTab("output")}
          className={`flex flex-col items-center justify-center p-1.5 rounded-lg font-label-tactical text-xs transition-colors cursor-pointer ${
            mobileTab === "output"
              ? "bg-gold-leaf text-on-primary font-bold shadow-sm"
              : "text-on-surface-variant hover:text-blood-accent"
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">
            query_stats
          </span>
          <span className="text-[10px] mt-0.5">Live Stats</span>
        </button>

        <button
          type="button"
          onClick={() => setMobileTab("input")}
          className={`flex flex-col items-center justify-center p-1.5 rounded-lg font-label-tactical text-xs transition-colors cursor-pointer ${
            mobileTab === "input"
              ? "bg-gold-leaf text-on-primary font-bold shadow-sm"
              : "text-on-surface-variant hover:text-blood-accent"
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">
            shield
          </span>
          <span className="text-[10px] mt-0.5">Forces & Eco</span>
        </button>

        <button
          type="button"
          onClick={() => setIsVoiceOpen(true)}
          className="flex flex-col items-center justify-center p-1.5 rounded-lg font-label-tactical text-xs text-on-surface-variant hover:text-blood-accent cursor-pointer"
        >
          <span className="material-symbols-outlined text-[20px]">
            mic
          </span>
          <span className="text-[10px] mt-0.5">Voice</span>
        </button>

        <button
          type="button"
          onClick={() => getTacticalRecommendation()}
          className="flex flex-col items-center justify-center p-1.5 rounded-lg font-label-tactical text-xs text-on-surface-variant hover:text-blood-accent cursor-pointer"
        >
          <span className="material-symbols-outlined text-[20px]">
            bolt
          </span>
          <span className="text-[10px] mt-0.5">Calculate</span>
        </button>
      </nav>
    </div>
  );
}
