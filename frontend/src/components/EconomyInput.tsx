"use client";

import React, { useState, useRef, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import { getResourceIconUrl } from "@/lib/assetDb";

interface NumberScrollInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange" | "value"> {
  value: number;
  step?: number;
  scrollStep?: number;
  min?: number;
  max?: number;
  onValueChange: (val: number) => void;
}

const NumberScrollInput: React.FC<NumberScrollInputProps> = ({
  value,
  step = 1,
  scrollStep = 1,
  min = 0,
  max,
  onValueChange,
  className = "",
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const onValueChangeRef = useRef(onValueChange);
  onValueChangeRef.current = onValueChange;

  const valueRef = useRef(value);
  valueRef.current = value;

  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const direction = e.deltaY < 0 ? 1 : -1;
      let next = valueRef.current + direction * scrollStep;
      if (min !== undefined) next = Math.max(min, next);
      if (max !== undefined) next = Math.min(max, next);
      valueRef.current = next;
      onValueChangeRef.current(next);
    };

    el.addEventListener("wheel", handleWheel, { passive: false });
    return () => {
      el.removeEventListener("wheel", handleWheel);
    };
  }, [scrollStep, min, max]);

  return (
    <input
      ref={inputRef}
      type="number"
      step={step}
      min={min}
      max={max}
      value={value}
      onChange={(e) => {
        const val = parseInt(e.target.value, 10);
        let next = isNaN(val) ? 0 : val;
        if (min !== undefined) next = Math.max(min, next);
        if (max !== undefined) next = Math.min(max, next);
        valueRef.current = next;
        onValueChange(next);
      }}
      className={`[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none ${className}`}
      {...props}
    />
  );
};

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
    <section className="bg-surface-container parchment-panel p-5 sm:p-6 rounded-lg w-full min-w-0 overflow-hidden">
      {/* Section Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 border-b border-outline-variant pb-4 min-w-0">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-full bg-gold-leaf text-on-primary flex items-center justify-center font-headline-md text-sm border border-surface-tint shrink-0">
            2
          </div>
          <h2 className="font-headline-lg text-lg sm:text-2xl text-primary uppercase tracking-wide font-bold truncate">
            Live Economy & Stockpile
          </h2>
        </div>
        <div className="font-label-tactical text-xs sm:text-sm text-on-surface-variant bg-surface-variant px-3 py-1 border border-outline-variant rounded shrink-0">
          Total Vills: <span className="font-bold text-primary">{totalVills}</span>
        </div>
      </div>

      {/* 4 Resource Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 min-w-0">
        {/* Food Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm min-w-0 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2 min-w-0">
            <div className="flex items-center gap-2 font-headline-md text-secondary font-bold text-sm sm:text-base min-w-0">
              <img
                src={getResourceIconUrl("food")}
                alt="Food"
                className="w-5 h-5 object-contain shrink-0"
              />
              <span className="truncate">FOOD</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical shrink-0">
              {pctFood}% eco
            </span>
          </div>

          <div className="space-y-4 min-w-0">
            {/* Food Current Bank */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label>Current Bank</label>
              </div>
              <NumberScrollInput
                value={snapshot.food}
                step={50}
                scrollStep={50}
                min={0}
                onValueChange={(val) => updateSnapshot({ food: val })}
                title="Scroll to change by 50"
                className="input-sunken bg-surface-bright w-full min-w-0 px-2.5 py-1.5 rounded text-secondary font-label-tactical font-bold text-center text-sm focus:outline-none"
              />
            </div>

            {/* Food Villagers */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label className="truncate">Farmers / Gatherers</label>
              </div>
              <div className="flex gap-1.5 items-center w-full min-w-0">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", -1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  -1
                </button>
                <NumberScrollInput
                  value={snapshot.vills_food}
                  step={1}
                  scrollStep={1}
                  min={0}
                  onValueChange={(val) => updateSnapshot({ vills_food: val })}
                  title="Scroll to change by 1"
                  className="input-sunken bg-surface-bright w-full min-w-0 flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_food", 1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Wood Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm min-w-0 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2 min-w-0">
            <div className="flex items-center gap-2 font-headline-md text-tertiary font-bold text-sm sm:text-base min-w-0">
              <img
                src={getResourceIconUrl("wood")}
                alt="Wood"
                className="w-5 h-5 object-contain shrink-0"
              />
              <span className="truncate">WOOD</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical shrink-0">
              {pctWood}% eco
            </span>
          </div>

          <div className="space-y-4 min-w-0">
            {/* Wood Current Bank */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label>Current Bank</label>
              </div>
              <NumberScrollInput
                value={snapshot.wood}
                step={50}
                scrollStep={50}
                min={0}
                onValueChange={(val) => updateSnapshot({ wood: val })}
                title="Scroll to change by 50"
                className="input-sunken bg-surface-bright w-full min-w-0 px-2.5 py-1.5 rounded text-tertiary font-label-tactical font-bold text-center text-sm focus:outline-none"
              />
            </div>

            {/* Wood Villagers */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label className="truncate">Lumberjacks</label>
              </div>
              <div className="flex gap-1.5 items-center w-full min-w-0">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", -1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  -1
                </button>
                <NumberScrollInput
                  value={snapshot.vills_wood}
                  step={1}
                  scrollStep={1}
                  min={0}
                  onValueChange={(val) => updateSnapshot({ vills_wood: val })}
                  title="Scroll to change by 1"
                  className="input-sunken bg-surface-bright w-full min-w-0 flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_wood", 1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Gold Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm min-w-0 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2 min-w-0">
            <div className="flex items-center gap-2 font-headline-md text-gold-leaf font-bold text-sm sm:text-base min-w-0">
              <img
                src={getResourceIconUrl("gold")}
                alt="Gold"
                className="w-5 h-5 object-contain shrink-0"
              />
              <span className="truncate">GOLD</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical shrink-0">
              {pctGold}% eco
            </span>
          </div>

          <div className="space-y-4 min-w-0">
            {/* Gold Current Bank */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label>Current Bank</label>
              </div>
              <NumberScrollInput
                value={snapshot.gold}
                step={50}
                scrollStep={50}
                min={0}
                onValueChange={(val) => updateSnapshot({ gold: val })}
                title="Scroll to change by 50"
                className="input-sunken bg-surface-bright w-full min-w-0 px-2.5 py-1.5 rounded text-gold-leaf font-label-tactical font-bold text-center text-sm focus:outline-none"
              />
            </div>

            {/* Gold Villagers */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label className="truncate">Gold Miners</label>
              </div>
              <div className="flex gap-1.5 items-center w-full min-w-0">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", -1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  -1
                </button>
                <NumberScrollInput
                  value={snapshot.vills_gold}
                  step={1}
                  scrollStep={1}
                  min={0}
                  onValueChange={(val) => updateSnapshot({ vills_gold: val })}
                  title="Scroll to change by 1"
                  className="input-sunken bg-surface-bright w-full min-w-0 flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_gold", 1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Stone Card */}
        <div className="bg-surface border border-outline-variant p-4 rounded hover-expand shadow-sm min-w-0 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4 border-b border-outline-variant pb-2 min-w-0">
            <div className="flex items-center gap-2 font-headline-md text-outline font-bold text-sm sm:text-base min-w-0">
              <img
                src={getResourceIconUrl("stone")}
                alt="Stone"
                className="w-5 h-5 object-contain shrink-0"
              />
              <span className="truncate">STONE</span>
            </div>
            <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical shrink-0">
              {pctStone}% eco
            </span>
          </div>

          <div className="space-y-4 min-w-0">
            {/* Stone Current Bank */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label>Current Bank</label>
              </div>
              <NumberScrollInput
                value={snapshot.stone}
                step={50}
                scrollStep={50}
                min={0}
                onValueChange={(val) => updateSnapshot({ stone: val })}
                title="Scroll to change by 50"
                className="input-sunken bg-surface-bright w-full min-w-0 px-2.5 py-1.5 rounded text-outline font-label-tactical font-bold text-center text-sm focus:outline-none"
              />
            </div>

            {/* Stone Villagers */}
            <div className="min-w-0">
              <div className="flex justify-between items-center text-xs text-on-surface-variant mb-1 font-medium min-w-0">
                <label className="truncate">Stone Miners</label>
              </div>
              <div className="flex gap-1.5 items-center w-full min-w-0">
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", -1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  -1
                </button>
                <NumberScrollInput
                  value={snapshot.vills_stone}
                  step={1}
                  scrollStep={1}
                  min={0}
                  onValueChange={(val) => updateSnapshot({ vills_stone: val })}
                  title="Scroll to change by 1"
                  className="input-sunken bg-surface-bright w-full min-w-0 flex-1 px-2 py-1 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleVillagerDelta("vills_stone", 1)}
                  className="bg-surface-variant border border-outline-variant px-2.5 py-1 rounded text-on-surface-variant text-xs hover:bg-outline-variant font-label-tactical cursor-pointer shrink-0 font-bold"
                >
                  +1
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Idle Villagers Card */}
      <div className="bg-surface border border-outline-variant p-4 rounded hover-expand w-full mb-6 shadow-sm min-w-0">
        <div className="flex justify-between items-center mb-3 border-b border-outline-variant pb-2 min-w-0">
          <div className="flex items-center gap-2 font-headline-md text-outline font-bold text-sm sm:text-base min-w-0">
            <img
              src={getResourceIconUrl("idle")}
              alt="Idle Villager"
              className="w-5 h-5 object-contain shrink-0"
            />
            <span className="truncate">IDLE VILLAGERS</span>
          </div>
          <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline-variant font-label-tactical shrink-0">
            {pctIdle}% eco
          </span>
        </div>
        <div className="flex gap-2 max-w-xs items-center w-full min-w-0">
          <button
            type="button"
            onClick={() => handleIdleDelta(-1)}
            className="bg-surface-variant border border-outline-variant px-3 py-1.5 rounded text-on-surface-variant font-label-tactical hover:bg-outline-variant cursor-pointer text-xs font-bold shrink-0"
          >
            -1
          </button>
          <NumberScrollInput
            value={idleVills}
            step={1}
            scrollStep={1}
            min={0}
            onValueChange={(val) => setIdleVills(val)}
            title="Scroll to change by 1"
            className="input-sunken bg-surface-bright w-full min-w-0 flex-1 px-3 py-1.5 rounded text-primary font-label-tactical font-bold text-center text-sm focus:outline-none"
          />
          <button
            type="button"
            onClick={() => handleIdleDelta(1)}
            className="bg-surface-variant border border-outline-variant px-3 py-1.5 rounded text-on-surface-variant font-label-tactical hover:bg-outline-variant cursor-pointer text-xs font-bold shrink-0"
          >
            +1
          </button>
        </div>
      </div>

      {/* Villager Distribution Breakdown Bar */}
      <div className="pt-5 border-t border-outline-variant min-w-0">
        <div className="flex flex-col sm:flex-row justify-between text-xs sm:text-sm font-label-tactical text-on-surface-variant mb-2 gap-1 min-w-0">
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
