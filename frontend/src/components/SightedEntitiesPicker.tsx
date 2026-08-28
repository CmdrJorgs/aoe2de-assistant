"use client";

import React, { useState } from "react";
import { useCoachStore } from "@/lib/store";
import { Eye, Plus, Minus, Trash2, ShieldAlert, Castle } from "lucide-react";

interface EntityDef {
  name: string;
  category: "infantry" | "cavalry" | "archer" | "siege" | "monk" | "building";
  icon: string;
  isUnique?: boolean;
}

const COMMON_ENTITIES: EntityDef[] = [
  // Cavalry
  { name: "Knight", category: "cavalry", icon: "♞" },
  { name: "Scout Cavalry", category: "cavalry", icon: "🐎" },
  { name: "Camel Rider", category: "cavalry", icon: "🐪" },
  { name: "Paladin", category: "cavalry", icon: "🏇" },
  { name: "Light Cavalry", category: "cavalry", icon: "🗡️" },
  { name: "Steppe Lancer", category: "cavalry", icon: "🪓" },

  // Archers
  { name: "Archer", category: "archer", icon: "🏹" },
  { name: "Crossbowman", category: "archer", icon: "🎯" },
  { name: "Arbalester", category: "archer", icon: "🎯" },
  { name: "Skirmisher", category: "archer", icon: "🛡️" },
  { name: "Cavalry Archer", category: "archer", icon: "🐎🏹" },
  { name: "Hand Cannoneer", category: "archer", icon: "💥" },

  // Infantry
  { name: "Spearman", category: "infantry", icon: "🔱" },
  { name: "Pikeman", category: "infantry", icon: "🔱" },
  { name: "Halberdier", category: "infantry", icon: "🔱" },
  { name: "Man-at-Arms", category: "infantry", icon: "⚔️" },
  { name: "Long Swordsman", category: "infantry", icon: "⚔️" },
  { name: "Champion", category: "infantry", icon: "🛡️⚔️" },
  { name: "Eagle Scout", category: "infantry", icon: "🦅" },
  { name: "Eagle Warrior", category: "infantry", icon: "🦅" },

  // Unique Units
  { name: "Berserk", category: "infantry", icon: "🪓", isUnique: true },
  { name: "Huskarl", category: "infantry", icon: "🛡️", isUnique: true },
  { name: "Longbowman", category: "archer", icon: "🏹", isUnique: true },
  { name: "Plumed Archer", category: "archer", icon: "🪶", isUnique: true },
  { name: "Mangudai", category: "archer", icon: "🏹🐎", isUnique: true },
  { name: "Conquistador", category: "cavalry", icon: "🔫", isUnique: true },
  { name: "Cataphract", category: "cavalry", icon: "🛡️♞", isUnique: true },
  { name: "Throwing Axeman", category: "infantry", icon: "🪓", isUnique: true },
  { name: "Janissary", category: "archer", icon: "💥", isUnique: true },
  { name: "Chu Ko Nu", category: "archer", icon: "🏹", isUnique: true },

  // Siege & Monks
  { name: "Mangonel", category: "siege", icon: "☄️" },
  { name: "Battering Ram", category: "siege", icon: "🪵" },
  { name: "Scorpion", category: "siege", icon: "🏹" },
  { name: "Trebuchet", category: "siege", icon: "🏰" },
  { name: "Bombard Cannon", category: "siege", icon: "💣" },
  { name: "Monk", category: "monk", icon: "✝️" },

  // Buildings
  { name: "Castle", category: "building", icon: "🏰" },
  { name: "Archery Range", category: "building", icon: "🏹" },
  { name: "Stable", category: "building", icon: "🛖" },
  { name: "Siege Workshop", category: "building", icon: "⚙️" },
  { name: "Barracks", category: "building", icon: "⚔️" },
  { name: "Monastery", category: "building", icon: "⛪" },
  { name: "Watch Tower", category: "building", icon: "🗼" },
];

export const SightedEntitiesPicker: React.FC = () => {
  const {
    snapshot,
    addSightedUnit,
    removeSightedUnit,
    addSightedBuilding,
    removeSightedBuilding,
    clearSightedUnits,
    clearSightedBuildings,
  } = useCoachStore();

  const [activeTab, setActiveTab] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredEntities = COMMON_ENTITIES.filter((e) => {
    const matchesTab = activeTab === "all" || e.category === activeTab;
    const matchesSearch = e.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTab && matchesSearch;
  });

  const sightedUnitsList = Object.entries(snapshot.sighted_enemy_units);
  const sightedBldgsList = Object.entries(snapshot.sighted_enemy_buildings);
  const totalSightedCount =
    sightedUnitsList.reduce((acc, [, c]) => acc + c, 0) +
    sightedBldgsList.reduce((acc, [, c]) => acc + c, 0);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold text-xs border border-amber-500/30">
            3
          </span>
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase">
            What Have You Sighted? (Fog of War)
          </h2>
        </div>
        <div className="flex items-center gap-2">
          {totalSightedCount > 0 && (
            <button
              type="button"
              onClick={() => {
                clearSightedUnits();
                clearSightedBuildings();
              }}
              className="flex items-center gap-1 text-[11px] text-rose-400 hover:text-rose-300 bg-rose-950/30 hover:bg-rose-950/60 border border-rose-900/40 px-2 py-1 rounded transition-colors"
            >
              <Trash2 className="w-3 h-3" />
              <span>Clear Sighted</span>
            </button>
          )}
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
            {totalSightedCount} Entities
          </span>
        </div>
      </div>

      {/* Active Sighted Summary Pills */}
      {totalSightedCount > 0 ? (
        <div className="mb-4 p-3 bg-slate-950/90 border border-rose-900/40 rounded-xl">
          <div className="flex items-center gap-1.5 text-xs text-rose-300 font-medium mb-2">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span>Observed Opponent Forces:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {sightedUnitsList.map(([uname, count]) => (
              <div
                key={uname}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-rose-950/50 border border-rose-800/60 text-rose-200 text-xs font-medium"
              >
                <span className="font-bold text-rose-400 font-mono">x{count}</span>
                <span>{uname}</span>
                <div className="flex items-center ml-1 gap-0.5">
                  <button
                    type="button"
                    onClick={() => removeSightedUnit(uname, 1)}
                    className="w-4 h-4 rounded bg-slate-900 hover:bg-rose-800 flex items-center justify-center text-slate-300 hover:text-white"
                  >
                    -
                  </button>
                  <button
                    type="button"
                    onClick={() => addSightedUnit(uname, 1)}
                    className="w-4 h-4 rounded bg-slate-900 hover:bg-rose-800 flex items-center justify-center text-slate-300 hover:text-white"
                  >
                    +
                  </button>
                </div>
              </div>
            ))}
            {sightedBldgsList.map(([bname, count]) => (
              <div
                key={bname}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-950/50 border border-amber-800/60 text-amber-200 text-xs font-medium"
              >
                <Castle className="w-3 h-3 text-amber-400" />
                <span className="font-bold text-amber-400 font-mono">x{count}</span>
                <span>{bname}</span>
                <div className="flex items-center ml-1 gap-0.5">
                  <button
                    type="button"
                    onClick={() => removeSightedBuilding(bname, 1)}
                    className="w-4 h-4 rounded bg-slate-900 hover:bg-amber-800 flex items-center justify-center text-slate-300 hover:text-white"
                  >
                    -
                  </button>
                  <button
                    type="button"
                    onClick={() => addSightedBuilding(bname, 1)}
                    className="w-4 h-4 rounded bg-slate-900 hover:bg-amber-800 flex items-center justify-center text-slate-300 hover:text-white"
                  >
                    +
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="mb-4 py-2.5 px-3 bg-slate-950/50 border border-slate-800/60 rounded-lg text-xs text-slate-400 flex items-center gap-2">
          <Eye className="w-4 h-4 text-slate-500" />
          <span>Click any unit or building below to record enemy forces seen in your scouting line of sight.</span>
        </div>
      )}

      {/* Category Tabs & Quick Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 mb-3">
        <div className="flex gap-1 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {[
            { id: "all", label: "All" },
            { id: "cavalry", label: "Cavalry" },
            { id: "archer", label: "Archers" },
            { id: "infantry", label: "Infantry" },
            { id: "siege", label: "Siege" },
            { id: "building", label: "Buildings" },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-amber-500 text-slate-950 font-bold"
                  : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Filter unit or building..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full sm:w-48 bg-slate-950 border border-slate-800 text-xs text-slate-200 px-2.5 py-1 rounded-lg focus:outline-none focus:border-amber-500"
        />
      </div>

      {/* Entity Picker Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-64 overflow-y-auto pr-1">
        {filteredEntities.map((entity) => {
          const isBuilding = entity.category === "building";
          const count = isBuilding
            ? snapshot.sighted_enemy_buildings[entity.name] || 0
            : snapshot.sighted_enemy_units[entity.name] || 0;
          const isSelected = count > 0;

          return (
            <div
              key={entity.name}
              className={`flex flex-col justify-between p-2 rounded-lg border transition-all text-left ${
                isSelected
                  ? isBuilding
                    ? "bg-amber-950/40 border-amber-500 text-amber-200"
                    : "bg-rose-950/40 border-rose-500 text-rose-200"
                  : "bg-slate-950 border-slate-800/80 hover:border-slate-700 text-slate-300"
              }`}
            >
              <div className="flex items-start justify-between mb-1">
                <span className="text-base">{entity.icon}</span>
                {isSelected && (
                  <span
                    className={`text-[10px] font-mono font-bold px-1 rounded ${
                      isBuilding ? "bg-amber-500 text-slate-950" : "bg-rose-500 text-slate-950"
                    }`}
                  >
                    x{count}
                  </span>
                )}
              </div>
              <div className="text-[11px] font-semibold truncate mb-2" title={entity.name}>
                {entity.name}
              </div>
              <div className="flex items-center justify-between gap-1 pt-1 border-t border-slate-900">
                <button
                  type="button"
                  onClick={() =>
                    isBuilding
                      ? removeSightedBuilding(entity.name, 1)
                      : removeSightedUnit(entity.name, 1)
                  }
                  disabled={count === 0}
                  className="p-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed text-slate-300"
                >
                  <Minus className="w-3 h-3" />
                </button>
                <button
                  type="button"
                  onClick={() =>
                    isBuilding
                      ? addSightedBuilding(entity.name, 1)
                      : addSightedUnit(entity.name, 1)
                  }
                  className="flex-1 py-1 rounded bg-slate-900 hover:bg-slate-800 flex items-center justify-center text-amber-400 font-bold text-xs"
                >
                  <Plus className="w-3 h-3" />
                </button>
                <button
                  type="button"
                  onClick={() =>
                    isBuilding
                      ? addSightedBuilding(entity.name, 5)
                      : addSightedUnit(entity.name, 5)
                  }
                  className="px-1.5 py-0.5 rounded bg-slate-900 hover:bg-slate-800 text-[10px] font-mono text-amber-400 font-bold"
                >
                  +5
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
