"use client";

import React from "react";
import { useCoachStore } from "@/lib/store";
import { Users, Wheat, Trees, Coins, Mountain, Plus, Minus } from "lucide-react";

export const EconomyInput: React.FC = () => {
  const { snapshot, updateSnapshot } = useCoachStore();

  const totalVills =
    snapshot.vills_total ||
    snapshot.vills_food + snapshot.vills_wood + snapshot.vills_gold + snapshot.vills_stone;

  const handleStockpileDelta = (res: "food" | "wood" | "gold" | "stone", delta: number) => {
    const nextVal = Math.max(0, snapshot[res] + delta);
    updateSnapshot({ [res]: nextVal });
  };

  const handleVillagerDelta = (res: "vills_food" | "vills_wood" | "vills_gold" | "vills_stone", delta: number) => {
    const nextVal = Math.max(0, snapshot[res] + delta);
    updateSnapshot({ [res]: nextVal });
  };

  // Percentage calculations for distribution bar
  const safeTotal = Math.max(1, totalVills);
  const pctFood = Math.round((snapshot.vills_food / safeTotal) * 100);
  const pctWood = Math.round((snapshot.vills_wood / safeTotal) * 100);
  const pctGold = Math.round((snapshot.vills_gold / safeTotal) * 100);
  const pctStone = Math.round((snapshot.vills_stone / safeTotal) * 100);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold text-xs border border-amber-500/30">
            2
          </span>
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase">
            Live Economy & Stockpile
          </h2>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-xs font-mono">
          <Users className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-400">Total Vills:</span>
          <span className="font-bold text-amber-300">{totalVills}</span>
        </div>
      </div>

      {/* Stockpiles & Villager Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Food Card */}
        <div className="bg-slate-950 border border-red-950/60 hover:border-red-900/80 rounded-xl p-3.5 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold text-red-400 uppercase tracking-wider">
              <Wheat className="w-4 h-4 text-red-500" /> Food
            </span>
            <span className="text-[11px] font-mono text-red-400/80 bg-red-950/40 px-1.5 py-0.5 rounded border border-red-900/40">
              {pctFood}% eco
            </span>
          </div>

          {/* Stockpile */}
          <div className="mb-3">
            <label className="text-[11px] text-slate-400 block mb-1">Current Bank</label>
            <div className="flex items-center gap-1">
              <input
                type="number"
                min={0}
                step={50}
                value={snapshot.food}
                onChange={(e) => updateSnapshot({ food: Math.max(0, parseInt(e.target.value) || 0) })}
                className="w-full bg-slate-900 border border-red-950 text-red-300 font-mono font-bold text-sm px-2.5 py-1.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-red-500"
              />
              <button
                type="button"
                onClick={() => handleStockpileDelta("food", 100)}
                className="px-2 py-1.5 bg-red-950/60 hover:bg-red-900/80 text-red-300 text-xs font-mono rounded"
              >
                +100
              </button>
            </div>
          </div>

          {/* Villagers on Food */}
          <div className="pt-2 border-t border-slate-900">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-400">Farmers / Gatherers</span>
              <span className="font-bold text-red-300 font-mono text-sm">{snapshot.vills_food}</span>
            </div>
            <div className="flex items-center justify-between gap-1">
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", -5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs rounded font-mono"
                >
                  -5
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", -1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", 1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-red-400 rounded"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", 5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-red-400 text-xs rounded font-mono"
                >
                  +5
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Wood Card */}
        <div className="bg-slate-950 border border-amber-950/60 hover:border-amber-900/80 rounded-xl p-3.5 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold text-amber-400 uppercase tracking-wider">
              <Trees className="w-4 h-4 text-amber-500" /> Wood
            </span>
            <span className="text-[11px] font-mono text-amber-400/80 bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-900/40">
              {pctWood}% eco
            </span>
          </div>

          <div className="mb-3">
            <label className="text-[11px] text-slate-400 block mb-1">Current Bank</label>
            <div className="flex items-center gap-1">
              <input
                type="number"
                min={0}
                step={50}
                value={snapshot.wood}
                onChange={(e) => updateSnapshot({ wood: Math.max(0, parseInt(e.target.value) || 0) })}
                className="w-full bg-slate-900 border border-amber-950 text-amber-300 font-mono font-bold text-sm px-2.5 py-1.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
              />
              <button
                type="button"
                onClick={() => handleStockpileDelta("wood", 100)}
                className="px-2 py-1.5 bg-amber-950/60 hover:bg-amber-900/80 text-amber-300 text-xs font-mono rounded"
              >
                +100
              </button>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-900">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-400">Lumberjacks</span>
              <span className="font-bold text-amber-300 font-mono text-sm">{snapshot.vills_wood}</span>
            </div>
            <div className="flex items-center justify-between gap-1">
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", -5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs rounded font-mono"
                >
                  -5
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", -1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", 1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-amber-400 rounded"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", 5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-amber-400 text-xs rounded font-mono"
                >
                  +5
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Gold Card */}
        <div className="bg-slate-950 border border-yellow-950/60 hover:border-yellow-900/80 rounded-xl p-3.5 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold text-yellow-400 uppercase tracking-wider">
              <Coins className="w-4 h-4 text-yellow-500" /> Gold
            </span>
            <span className="text-[11px] font-mono text-yellow-400/80 bg-yellow-950/40 px-1.5 py-0.5 rounded border border-yellow-900/40">
              {pctGold}% eco
            </span>
          </div>

          <div className="mb-3">
            <label className="text-[11px] text-slate-400 block mb-1">Current Bank</label>
            <div className="flex items-center gap-1">
              <input
                type="number"
                min={0}
                step={50}
                value={snapshot.gold}
                onChange={(e) => updateSnapshot({ gold: Math.max(0, parseInt(e.target.value) || 0) })}
                className="w-full bg-slate-900 border border-yellow-950 text-yellow-300 font-mono font-bold text-sm px-2.5 py-1.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-yellow-500"
              />
              <button
                type="button"
                onClick={() => handleStockpileDelta("gold", 100)}
                className="px-2 py-1.5 bg-yellow-950/60 hover:bg-yellow-900/80 text-yellow-300 text-xs font-mono rounded"
              >
                +100
              </button>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-900">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-400">Gold Miners</span>
              <span className="font-bold text-yellow-300 font-mono text-sm">{snapshot.vills_gold}</span>
            </div>
            <div className="flex items-center justify-between gap-1">
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", -5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs rounded font-mono"
                >
                  -5
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", -1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", 1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-yellow-400 rounded"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", 5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-yellow-400 text-xs rounded font-mono"
                >
                  +5
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Stone Card */}
        <div className="bg-slate-950 border border-slate-800/80 hover:border-slate-700 rounded-xl p-3.5 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <Mountain className="w-4 h-4 text-slate-400" /> Stone
            </span>
            <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
              {pctStone}% eco
            </span>
          </div>

          <div className="mb-3">
            <label className="text-[11px] text-slate-400 block mb-1">Current Bank</label>
            <div className="flex items-center gap-1">
              <input
                type="number"
                min={0}
                step={50}
                value={snapshot.stone}
                onChange={(e) => updateSnapshot({ stone: Math.max(0, parseInt(e.target.value) || 0) })}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 font-mono font-bold text-sm px-2.5 py-1.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-slate-500"
              />
              <button
                type="button"
                onClick={() => handleStockpileDelta("stone", 100)}
                className="px-2 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-mono rounded"
              >
                +100
              </button>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-900">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-400">Stone Miners</span>
              <span className="font-bold text-slate-200 font-mono text-sm">{snapshot.vills_stone}</span>
            </div>
            <div className="flex items-center justify-between gap-1">
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", -5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs rounded font-mono"
                >
                  -5
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", -1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", 1)}
                  className="p-1 bg-slate-900 hover:bg-slate-800 text-slate-200 rounded"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", 5)}
                  className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs rounded font-mono"
                >
                  +5
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Villager Distribution Bar */}
      <div className="mt-4 pt-3 border-t border-slate-800/60">
        <div className="flex justify-between items-center text-xs text-slate-400 mb-1.5">
          <span>Villager Distribution Breakdown</span>
          <span className="font-mono text-slate-300">
            {snapshot.vills_food}F / {snapshot.vills_wood}W / {snapshot.vills_gold}G / {snapshot.vills_stone}S
          </span>
        </div>
        <div className="h-2.5 w-full bg-slate-950 rounded-full overflow-hidden flex border border-slate-800">
          <div style={{ width: `${pctFood}%` }} className="bg-red-500 transition-all duration-300" title={`Food: ${pctFood}%`} />
          <div style={{ width: `${pctWood}%` }} className="bg-amber-500 transition-all duration-300" title={`Wood: ${pctWood}%`} />
          <div style={{ width: `${pctGold}%` }} className="bg-yellow-400 transition-all duration-300" title={`Gold: ${pctGold}%`} />
          <div style={{ width: `${pctStone}%` }} className="bg-slate-400 transition-all duration-300" title={`Stone: ${pctStone}%`} />
        </div>
      </div>
    </div>
  );
};
