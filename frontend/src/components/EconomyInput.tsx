"use client";

import React, { useState } from "react";
import { useCoachStore } from "@/lib/store";
import { getResourceIconUrl } from "@/lib/assetDb";

export const EconomyInput: React.FC = () => {
  const { snapshot, updateSnapshot } = useCoachStore();
  const [idleVills, setIdleVills] = useState<number>(0);

  const totalVills =
    snapshot.vills_total ||
    snapshot.vills_food +
      snapshot.vills_wood +
      snapshot.vills_gold +
      snapshot.vills_stone +
      idleVills;

  const handleStockpileDelta = (
    res: "food" | "wood" | "gold" | "stone",
    delta: number
  ) => {
    const nextVal = Math.max(0, snapshot[res] + delta);
    updateSnapshot({ [res]: nextVal });
  };

  const handleVillagerDelta = (
    res: "vills_food" | "vills_wood" | "vills_gold" | "vills_stone",
    delta: number
  ) => {
    const nextVal = Math.max(0, snapshot[res] + delta);
    updateSnapshot({ [res]: nextVal });
  };

  const handleIdleDelta = (delta: number) => {
    setIdleVills((prev) => Math.max(0, prev + delta));
  };

  // Percentage calculations
  const safeTotal = Math.max(1, totalVills);
  const pctFood = Math.round((snapshot.vills_food / safeTotal) * 100);
  const pctWood = Math.round((snapshot.vills_wood / safeTotal) * 100);
  const pctGold = Math.round((snapshot.vills_gold / safeTotal) * 100);
  const pctStone = Math.round((snapshot.vills_stone / safeTotal) * 100);
  const pctIdle = Math.round((idleVills / safeTotal) * 100);

  return (
    <section className="bg-surface-container parchment-panel p-5 sm:p-6 rounded-lg">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-6 border-b border-outline-variant pb-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gold-leaf text-on-primary flex items-center justify-center font-headline-md text-sm border border-surface-tint shrink-0">
            2
          </div>
          <h2 className="font-headline-lg text-lg sm:text-2xl text-primary uppercase tracking-wide font-bold">
            Live Economy & Stockpile
          </h2>
        </div>
        <div className="font-label-tactical text-xs sm:text-sm text-on-surface-variant bg-surface-variant px-3 py-1 border border-outline-variant rounded">
          Total Vills: <span className="font-bold text-primary">{totalVills}</span>
        </div>
      </div>

      {/* 4 Resource Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6 mb-6">
        {/* Food Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2 font-headline-md text-secondary font-bold text-sm sm:text-base">
              <img
                src={getResourceIconUrl("food")}
                alt="Food"
                className="w-5 h-5 object-contain"
              />
              <span>FOOD</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical">
              {pctFood}% eco
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs text-on-surface-variant mb-1 block font-medium">
                Current Bank
              </label>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("food", -100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -100
                </button>
                <input
                  type="number"
                  min={0}
                  step={50}
                  value={snapshot.food}
                  onChange={(e) =>
                    updateSnapshot({
                      food: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1.5 rounded text-secondary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("food", 100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +100
                </button>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-on-surface-variant mb-1 font-medium">
                <label>Farmers / Gatherers</label>
              </div>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", -1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -1
                </button>
                <input
                  type="number"
                  min={0}
                  value={snapshot.vills_food}
                  onChange={(e) =>
                    updateSnapshot({
                      vills_food: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", 1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Wood Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2 font-headline-md text-tertiary font-bold text-sm sm:text-base">
              <img
                src={getResourceIconUrl("wood")}
                alt="Wood"
                className="w-5 h-5 object-contain"
              />
              <span>WOOD</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical">
              {pctWood}% eco
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs text-on-surface-variant mb-1 block font-medium">
                Current Bank
              </label>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("wood", -100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -100
                </button>
                <input
                  type="number"
                  min={0}
                  step={50}
                  value={snapshot.wood}
                  onChange={(e) =>
                    updateSnapshot({
                      wood: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1.5 rounded text-tertiary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("wood", 100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +100
                </button>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-on-surface-variant mb-1 font-medium">
                <label>Lumberjacks</label>
              </div>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", -1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -1
                </button>
                <input
                  type="number"
                  min={0}
                  value={snapshot.vills_wood}
                  onChange={(e) =>
                    updateSnapshot({
                      vills_wood: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", 1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Gold Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2 font-headline-md text-gold-leaf font-bold text-sm sm:text-base">
              <img
                src={getResourceIconUrl("gold")}
                alt="Gold"
                className="w-5 h-5 object-contain"
              />
              <span>GOLD</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical">
              {pctGold}% eco
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs text-on-surface-variant mb-1 block font-medium">
                Current Bank
              </label>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("gold", -100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -100
                </button>
                <input
                  type="number"
                  min={0}
                  step={50}
                  value={snapshot.gold}
                  onChange={(e) =>
                    updateSnapshot({
                      gold: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1.5 rounded text-gold-leaf font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("gold", 100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +100
                </button>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-on-surface-variant mb-1 font-medium">
                <label>Gold Miners</label>
              </div>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", -1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -1
                </button>
                <input
                  type="number"
                  min={0}
                  value={snapshot.vills_gold}
                  onChange={(e) =>
                    updateSnapshot({
                      vills_gold: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", 1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Stone Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2 font-headline-md text-outline font-bold text-sm sm:text-base">
              <img
                src={getResourceIconUrl("stone")}
                alt="Stone"
                className="w-5 h-5 object-contain"
              />
              <span>STONE</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical">
              {pctStone}% eco
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs text-on-surface-variant mb-1 block font-medium">
                Current Bank
              </label>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("stone", -100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -100
                </button>
                <input
                  type="number"
                  min={0}
                  step={50}
                  value={snapshot.stone}
                  onChange={(e) =>
                    updateSnapshot({
                      stone: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1.5 rounded text-outline font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleStockpileDelta("stone", 100)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +100
                </button>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-on-surface-variant mb-1 font-medium">
                <label>Stone Miners</label>
              </div>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", -1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  -1
                </button>
                <input
                  type="number"
                  min={0}
                  value={snapshot.vills_stone}
                  onChange={(e) =>
                    updateSnapshot({
                      vills_stone: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className="input-sunken bg-surface-bright flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", 1)}
                  className="bg-surface-variant border border-outline-variant px-3 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Idle Villagers Card */}
      <div className="bg-surface border border-outline-variant p-4 rounded hover-expand w-full mb-6 shadow-sm">
        <div className="flex justify-between items-center mb-3 border-b border-outline-variant pb-2">
          <div className="flex items-center gap-2 font-headline-md text-outline font-bold text-sm sm:text-base">
            <img
              src={getResourceIconUrl("idle")}
              alt="Idle Villager"
              className="w-5 h-5 object-contain"
            />
            <span>IDLE VILLAGERS</span>
          </div>
          <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical">
            {pctIdle}% eco
          </span>
        </div>
        <div className="flex gap-2 max-w-xs">
          <button
            type="button"
            onClick={() => handleIdleDelta(-1)}
            className="bg-surface-variant border border-outline-variant px-4 py-2 rounded text-on-surface-variant font-label-tactical hover:bg-outline-variant cursor-pointer text-xs font-bold"
          >
            -1
          </button>
          <div className="input-sunken bg-surface-bright flex-1 px-4 py-2 rounded text-primary font-label-tactical font-bold text-center flex items-center justify-center text-sm">
            {idleVills}
          </div>
          <button
            type="button"
            onClick={() => handleIdleDelta(1)}
            className="bg-surface-variant border border-outline-variant px-4 py-2 rounded text-on-surface-variant font-label-tactical hover:bg-outline-variant cursor-pointer text-xs font-bold"
          >
            +1
          </button>
        </div>
      </div>

      {/* Villager Distribution Breakdown Bar */}
      <div className="pt-5 border-t border-outline-variant">
        <div className="flex flex-col sm:flex-row justify-between text-xs sm:text-sm font-label-tactical text-on-surface-variant mb-2 gap-1">
          <span className="font-semibold">Villager Distribution Breakdown</span>
          <span className="font-bold text-primary">
            {snapshot.vills_food}F / {snapshot.vills_wood}W / {snapshot.vills_gold}G /{" "}
            {snapshot.vills_stone}S / {idleVills}I
          </span>
        </div>
        <div className="h-3.5 w-full flex rounded-full overflow-hidden border border-outline-variant shadow-inner bg-surface">
          <div
            className="bg-secondary h-full transition-all duration-200"
            style={{ width: `${pctFood}%` }}
            title={`Food: ${pctFood}%`}
          />
          <div
            className="bg-tertiary h-full transition-all duration-200"
            style={{ width: `${pctWood}%` }}
            title={`Wood: ${pctWood}%`}
          />
          <div
            className="bg-gold-leaf h-full transition-all duration-200"
            style={{ width: `${pctGold}%` }}
            title={`Gold: ${pctGold}%`}
          />
          <div
            className="bg-outline h-full transition-all duration-200"
            style={{ width: `${pctStone}%` }}
            title={`Stone: ${pctStone}%`}
          />
          <div
            className="bg-slate-400 h-full transition-all duration-200"
            style={{ width: `${pctIdle}%` }}
            title={`Idle: ${pctIdle}%`}
          />
        </div>
      </div>
    </section>
  );
};
