"use client";

import React, { useState, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import { Header } from "@/components/Header";
import { MatchSetup } from "@/components/MatchSetup";
import { EconomyInput } from "@/components/EconomyInput";
import { SightedEntitiesPicker } from "@/components/SightedEntitiesPicker";
import { TacticalDashboard } from "@/components/TacticalDashboard";
import { VoiceInputModal } from "@/components/VoiceInputModal";
import { Zap, Mic, AlertCircle, RefreshCw, Swords } from "lucide-react";

export default function Home() {
  const {
    recommendation,
    isLoading,
    error,
    getTacticalRecommendation,
    loadMetadata,
  } = useCoachStore();

  const [isVoiceOpen, setIsVoiceOpen] = useState<boolean>(false);

  useEffect(() => {
    loadMetadata();
  }, [loadMetadata]);

  // Trigger initial recommendation if none loaded
  useEffect(() => {
    if (!recommendation && !isLoading) {
      getTacticalRecommendation();
    }
  }, [recommendation, isLoading, getTacticalRecommendation]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      {/* App Header */}
      <Header onOpenVoice={() => setIsVoiceOpen(true)} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        {/* Rapid Voice Banner & Quick Trigger Bar */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
              <Zap className="w-5 h-5 fill-current" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <span>30-Second Mid-Game Wizard</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                  FAST INPUT
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Update match state or tap microphone for instant voice analysis
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            {/* Voice Input Button */}
            <button
              type="button"
              onClick={() => setIsVoiceOpen(true)}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-amber-500/40 text-amber-300 hover:text-amber-200 text-xs font-bold transition-all shadow-md"
            >
              <Mic className="w-4 h-4 text-amber-400" />
              <span>Voice Update</span>
            </button>

            {/* Main Action Button */}
            <button
              type="button"
              onClick={() => getTacticalRecommendation()}
              disabled={isLoading}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-black uppercase tracking-wider shadow-lg shadow-amber-500/25 gold-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Computing...</span>
                </>
              ) : (
                <>
                  <Swords className="w-4 h-4 fill-current" />
                  <span>Get Tactical Advice</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-200 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <div className="flex-1">
              <strong>Recommendation Error:</strong> {error}
            </div>
            <button
              type="button"
              onClick={() => getTacticalRecommendation()}
              className="px-3 py-1 bg-rose-900 hover:bg-rose-800 rounded font-semibold text-[11px]"
            >
              Retry
            </button>
          </div>
        )}

        {/* Wizard Input Steps (Grid Layout) */}
        <div className="space-y-4">
          <MatchSetup />
          <EconomyInput />
          <SightedEntitiesPicker />
        </div>

        {/* Tactical Recommendation Dashboard */}
        <div className="pt-4 border-t border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs border border-emerald-500/30">
                ✓
              </span>
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wide">
                Live Tactical Output & Coaching
              </h2>
            </div>
            {recommendation && (
              <span className="text-xs font-mono text-slate-400">
                Last updated at {new Date().toLocaleTimeString()}
              </span>
            )}
          </div>

          {isLoading && !recommendation ? (
            <div className="p-12 rounded-2xl bg-slate-900/60 border border-slate-800 text-center flex flex-col items-center justify-center space-y-3">
              <div className="w-12 h-12 rounded-full border-2 border-amber-500/20 border-t-amber-500 animate-spin flex items-center justify-center">
                <Swords className="w-5 h-5 text-amber-400" />
              </div>
              <span className="text-sm font-semibold text-slate-300">
                Synthesizing ML strategy, counter-matrix & verified coaching advice...
              </span>
            </div>
          ) : recommendation ? (
            <TacticalDashboard data={recommendation} />
          ) : null}
        </div>
      </main>

      {/* Voice Input Modal */}
      <VoiceInputModal isOpen={isVoiceOpen} onClose={() => setIsVoiceOpen(false)} />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AoE2 Coach AI — Real-Time Strategic Decision Support</span>
          <span>Age of Empires II: DE is a trademark of Microsoft Corp. Community AI Coach.</span>
        </div>
      </footer>
    </div>
  );
}
