"use client";

import React from "react";
import { useCoachStore } from "@/lib/store";
import { AgeNumber } from "@/types/coach";
import { Shield, Crosshair, Crown, Clock, Award } from "lucide-react";

const AGES: { id: AgeNumber; name: string; icon: string }[] = [
  { id: 1, name: "Dark Age", icon: "🛖" },
  { id: 2, name: "Feudal Age", icon: "🏹" },
  { id: 3, name: "Castle Age", icon: "🏰" },
  { id: 4, name: "Imperial Age", icon: "👑" },
];

const ELO_PRESETS = [800, 1000, 1200, 1400, 1600, 1800];

export const MatchSetup: React.FC = () => {
  const { snapshot, updateSnapshot, civs } = useCoachStore();

  const handleCivChange = (type: "player" | "opponent", civName: string) => {
    if (type === "player") updateSnapshot({ player_civ: civName });
    else updateSnapshot({ opponent_civ: civName });
  };

  const handleAgeChange = (age: AgeNumber) => {
    updateSnapshot({ current_age: age });
  };

  const handleEloChange = (elo: number) => {
    updateSnapshot({ player_elo: Math.max(400, Math.min(3000, elo)) });
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold text-xs border border-amber-500/30">
            1
          </span>
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase">
            Match Context & Setup
          </h2>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          {snapshot.player_civ} vs {snapshot.opponent_civ}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Player Civ */}
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1.5 flex items-center gap-1.5">
            <Crown className="w-3.5 h-3.5 text-amber-400" />
            <span>Your Civilization</span>
          </label>
          <div className="relative">
            <select
              value={snapshot.player_civ}
              onChange={(e) => handleCivChange("player", e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-amber-300 font-medium focus:ring-1 focus:ring-amber-500 focus:border-amber-500 outline-none cursor-pointer"
            >
              {civs.length > 0 ? (
                civs.map((c) => (
                  <option key={c.id} value={c.name} className="bg-slate-950 text-slate-200">
                    {c.name}
                  </option>
                ))
              ) : (
                ["Franks", "Britons", "Vikings", "Goths", "Teutons", "Mongols", "Mayans", "Aztecs"].map((c) => (
                  <option key={c} value={c} className="bg-slate-950 text-slate-200">
                    {c}
                  </option>
                ))
              )}
            </select>
          </div>
        </div>

        {/* Opponent Civ */}
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1.5 flex items-center gap-1.5">
            <Crosshair className="w-3.5 h-3.5 text-rose-400" />
            <span>Opponent Civilization</span>
          </label>
          <div className="relative">
            <select
              value={snapshot.opponent_civ}
              onChange={(e) => handleCivChange("opponent", e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-rose-300 font-medium focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none cursor-pointer"
            >
              {civs.length > 0 ? (
                civs.map((c) => (
                  <option key={c.id} value={c.name} className="bg-slate-950 text-slate-200">
                    {c.name}
                  </option>
                ))
              ) : (
                ["Vikings", "Franks", "Britons", "Goths", "Teutons", "Mongols", "Mayans", "Aztecs"].map((c) => (
                  <option key={c} value={c} className="bg-slate-950 text-slate-200">
                    {c}
                  </option>
                ))
              )}
            </select>
          </div>
        </div>

        {/* Player ELO */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-yellow-400" />
              <span>Player ELO</span>
            </label>
            <span className="text-xs font-bold text-amber-400 font-mono">
              {snapshot.player_elo}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <input
              type="number"
              min={400}
              max={3000}
              step={25}
              value={snapshot.player_elo}
              onChange={(e) => handleEloChange(parseInt(e.target.value) || 1000)}
              className="w-20 bg-slate-950 border border-slate-700/80 rounded-lg px-2 py-1.5 text-xs text-slate-200 font-mono text-center focus:ring-1 focus:ring-amber-500 outline-none"
            />
            <div className="flex gap-1 flex-1 overflow-x-auto">
              {ELO_PRESETS.map((elo) => (
                <button
                  key={elo}
                  type="button"
                  onClick={() => handleEloChange(elo)}
                  className={`px-1.5 py-1 text-[10px] font-mono rounded transition-colors ${
                    snapshot.player_elo === elo
                      ? "bg-amber-500 text-slate-950 font-bold"
                      : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                  }`}
                >
                  {elo}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Game Time */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Game Time</span>
            </label>
            <span className="text-xs font-bold text-cyan-300 font-mono">
              {Math.floor(snapshot.game_time_minutes)}:
              {String(Math.round((snapshot.game_time_minutes % 1) * 60)).padStart(2, "0")}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="range"
              min={1}
              max={60}
              step={0.5}
              value={snapshot.game_time_minutes}
              onChange={(e) => updateSnapshot({ game_time_minutes: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <button
              type="button"
              onClick={() => updateSnapshot({ game_time_minutes: Math.max(1, snapshot.game_time_minutes - 1) })}
              className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded"
            >
              -1m
            </button>
            <button
              type="button"
              onClick={() => updateSnapshot({ game_time_minutes: snapshot.game_time_minutes + 1 })}
              className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded"
            >
              +1m
            </button>
          </div>
        </div>
      </div>

      {/* Age Selector Tabs */}
      <div className="mt-4 pt-3 border-t border-slate-800/60">
        <label className="block text-xs font-medium text-slate-400 mb-2 flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-amber-400" />
          <span>Current Game Age</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {AGES.map((a) => {
            const isSelected = snapshot.current_age === a.id;
            return (
              <button
                key={a.id}
                type="button"
                onClick={() => handleAgeChange(a.id)}
                className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg border text-xs font-semibold transition-all ${
                  isSelected
                    ? "bg-amber-500/15 border-amber-500 text-amber-300 shadow-sm shadow-amber-500/20"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                }`}
              >
                <span className="text-base">{a.icon}</span>
                <span>{a.name}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
