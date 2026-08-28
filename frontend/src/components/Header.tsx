"use client";

import React, { useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import { Swords, Activity, RotateCcw, Sparkles, Mic } from "lucide-react";

export const Header: React.FC<{ onOpenVoice: () => void }> = ({ onOpenVoice }) => {
  const { health, checkHealth, resetSnapshot, presets, applyPreset, selectedPresetId } =
    useCoachStore();

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40 px-4 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand & Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 p-0.5 shadow-lg shadow-amber-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[7px] flex items-center justify-center">
              <Swords className="w-5 h-5 text-amber-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-amber-400 tracking-wide">
                AoE2 COACH <span className="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">AI PRO</span>
              </h1>
            </div>
            <p className="text-xs text-slate-400">Real-Time Tactical & Strategic Decision Engine</p>
          </div>
        </div>

        {/* Quick Presets & Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Voice Button */}
          <button
            onClick={onOpenVoice}
            title="Voice input"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-xs font-bold text-amber-400 transition-colors"
          >
            <Mic className="w-3.5 h-3.5" />
            <span>Voice Update</span>
          </button>

          {/* Preset Selector */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400 hidden sm:inline">Scenario:</span>
            <select
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer pr-2"
              value={selectedPresetId || ""}
              onChange={(e) => {
                const p = presets.find((x) => x.id === e.target.value);
                if (p) applyPreset(p);
              }}
            >
              <option value="" disabled className="bg-slate-900 text-slate-400">
                Load Preset Scenario...
              </option>
              {presets.map((p) => (
                <option key={p.id} value={p.id} className="bg-slate-900 text-slate-200">
                  {p.title} ({p.difficulty})
                </option>
              ))}
            </select>
          </div>

          {/* Reset Button */}
          <button
            onClick={resetSnapshot}
            title="Reset match snapshot"
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>

          {/* Health & Engine Status */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <div
              className={`flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium border ${
                health?.status === "healthy"
                  ? "bg-emerald-950/40 border-emerald-800/60 text-emerald-400"
                  : "bg-rose-950/40 border-rose-800/60 text-rose-400"
              }`}
            >
              <Activity className="w-3 h-3" />
              <span>{health?.status === "healthy" ? "ONNX Engine Ready" : "Connecting..."}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
