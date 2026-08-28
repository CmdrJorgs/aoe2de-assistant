"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { CombatSimResponse } from "@/types/coach";
import { useCoachStore } from "@/lib/store";
import { Swords, Mountain, Play, Trophy } from "lucide-react";

export const CombatSimulatorWidget: React.FC = () => {
  const { snapshot, units } = useCoachStore();

  const [attackerUnit, setAttackerUnit] = useState<string>("Knight");
  const [attackerCount, setAttackerCount] = useState<number>(10);
  const [defenderUnit, setDefenderUnit] = useState<string>("Pikeman");
  const [defenderCount, setDefenderCount] = useState<number>(12);
  const [elevationDiff, setElevationDiff] = useState<number>(0);
  const [result, setResult] = useState<CombatSimResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  const unitOptions = units.length > 0 ? units.map((u) => u.name) : ["Knight", "Pikeman", "Crossbowman", "Berserk", "Mangonel", "Camel Rider", "Huskarl"];

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const res = await api.simulateCombat({
        attacker_unit: attackerUnit,
        attacker_count: attackerCount,
        attacker_civ: snapshot.player_civ,
        defender_unit: defenderUnit,
        defender_count: defenderCount,
        defender_civ: snapshot.opponent_civ,
        elevation_diff: elevationDiff,
      });
      setResult(res);
    } catch (e) {
      console.error("Combat simulation error:", e);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
            <Swords className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
            Real-Time Combat & Duel Simulator
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          Exact Armor & Class Damage Calculator
        </span>
      </div>

      {/* Simulator Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Attacker (Player) */}
        <div className="bg-slate-950 border border-amber-900/40 rounded-xl p-3">
          <div className="text-xs font-bold text-amber-400 mb-2 flex items-center justify-between">
            <span>YOUR FORCES ({snapshot.player_civ})</span>
            <span className="text-[10px] font-mono text-slate-400">Attacker</span>
          </div>
          <div className="space-y-2">
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Unit Type:</label>
              <select
                value={attackerUnit}
                onChange={(e) => setAttackerUnit(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 p-2 rounded-lg outline-none cursor-pointer"
              >
                {unitOptions.map((u) => (
                  <option key={u} value={u} className="bg-slate-900">
                    {u}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Army Count: {attackerCount}</label>
              <input
                type="number"
                min={1}
                max={100}
                value={attackerCount}
                onChange={(e) => setAttackerCount(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-amber-300 font-mono font-bold p-1.5 rounded-lg text-center"
              />
            </div>
          </div>
        </div>

        {/* Engagement Modifiers */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="text-xs font-bold text-slate-300 mb-2 text-center">
            TERRAIN & ELEVATION
          </div>
          <div className="space-y-2 text-center">
            <div className="flex justify-center gap-1">
              <button
                type="button"
                onClick={() => setElevationDiff(1)}
                className={`flex-1 py-1.5 px-2 rounded text-xs font-semibold flex items-center justify-center gap-1 border transition-colors ${
                  elevationDiff === 1
                    ? "bg-amber-500 text-slate-950 border-amber-400 font-bold"
                    : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
                }`}
              >
                <Mountain className="w-3 h-3" />
                <span>+25% Hill</span>
              </button>
              <button
                type="button"
                onClick={() => setElevationDiff(0)}
                className={`flex-1 py-1.5 px-2 rounded text-xs font-semibold border transition-colors ${
                  elevationDiff === 0
                    ? "bg-slate-700 text-slate-100 border-slate-600 font-bold"
                    : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
                }`}
              >
                Flat Ground
              </button>
              <button
                type="button"
                onClick={() => setElevationDiff(-1)}
                className={`flex-1 py-1.5 px-2 rounded text-xs font-semibold flex items-center justify-center gap-1 border transition-colors ${
                  elevationDiff === -1
                    ? "bg-rose-600 text-white border-rose-500 font-bold"
                    : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
                }`}
              >
                <Mountain className="w-3 h-3 rotate-180" />
                <span>-25% Low</span>
              </button>
            </div>

            <button
              type="button"
              onClick={handleSimulate}
              disabled={isSimulating}
              className="w-full mt-2 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-amber-500/20 transition-all"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isSimulating ? "Simulating Battle..." : "Run Combat Duel"}</span>
            </button>
          </div>
        </div>

        {/* Defender (Opponent) */}
        <div className="bg-slate-950 border border-rose-900/40 rounded-xl p-3">
          <div className="text-xs font-bold text-rose-400 mb-2 flex items-center justify-between">
            <span>ENEMY FORCES ({snapshot.opponent_civ})</span>
            <span className="text-[10px] font-mono text-slate-400">Defender</span>
          </div>
          <div className="space-y-2">
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Unit Type:</label>
              <select
                value={defenderUnit}
                onChange={(e) => setDefenderUnit(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 p-2 rounded-lg outline-none cursor-pointer"
              >
                {unitOptions.map((u) => (
                  <option key={u} value={u} className="bg-slate-900">
                    {u}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Army Count: {defenderCount}</label>
              <input
                type="number"
                min={1}
                max={100}
                value={defenderCount}
                onChange={(e) => setDefenderCount(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-rose-300 font-mono font-bold p-1.5 rounded-lg text-center"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Simulation Result Output */}
      {result && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 animate-in fade-in">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-bold text-slate-200">
                Predicted Winner: <span className="text-amber-400 font-mono">{result.simulated_winner}</span>
              </span>
            </div>
            <span className="text-xs font-mono text-cyan-400 font-semibold">
              Time to Kill: {result.time_to_kill_seconds}s
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 text-center">
            <div className="p-2 bg-slate-900 rounded-lg">
              <span className="text-[10px] text-slate-400 block">Your Damage/Hit</span>
              <span className="text-xs font-mono font-bold text-amber-300">
                {result.single_hit_attacker_to_defender} HP
              </span>
            </div>
            <div className="p-2 bg-slate-900 rounded-lg">
              <span className="text-[10px] text-slate-400 block">Enemy Damage/Hit</span>
              <span className="text-xs font-mono font-bold text-rose-300">
                {result.single_hit_defender_to_attacker} HP
              </span>
            </div>
            <div className="p-2 bg-slate-900 rounded-lg">
              <span className="text-[10px] text-slate-400 block">Remaining Forces</span>
              <span className="text-xs font-mono font-bold text-emerald-300">
                {result.remaining_attackers} vs {result.remaining_defenders}
              </span>
            </div>
            <div className="p-2 bg-slate-900 rounded-lg">
              <span className="text-[10px] text-slate-400 block">Cost Efficiency Ratio</span>
              <span className="text-xs font-mono font-bold text-cyan-300">
                {result.cost_efficiency_ratio}x
              </span>
            </div>
          </div>

          <p className="text-xs text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
            {result.tactical_summary}
          </p>
        </div>
      )}
    </div>
  );
};
