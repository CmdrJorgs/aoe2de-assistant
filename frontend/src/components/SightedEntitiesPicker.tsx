"use client";

import React, { useState, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import {
  getAssetDatabase,
  getAssetFromCatalog,
  AssetDatabase,
} from "@/lib/assetDb";
import { Trash2 } from "lucide-react";

interface GridEntity {
  name: string;
  category: "military" | "economy" | "building";
  type: "unit" | "building";
}

const TACTICAL_ENTITIES: GridEntity[] = [
  // Military Units
  { name: "Militia", category: "military", type: "unit" },
  { name: "Spearman", category: "military", type: "unit" },
  { name: "Eagle Scout", category: "military", type: "unit" },
  { name: "Archer", category: "military", type: "unit" },
  { name: "Skirmisher", category: "military", type: "unit" },
  { name: "Cavalry Archer", category: "military", type: "unit" },
  { name: "Scout Cavalry", category: "military", type: "unit" },
  { name: "Knight", category: "military", type: "unit" },
  { name: "Camel", category: "military", type: "unit" },
  { name: "Battering Ram", category: "military", type: "unit" },
  { name: "Mangonel", category: "military", type: "unit" },
  { name: "Scorpion", category: "military", type: "unit" },
  { name: "Trebuchet", category: "military", type: "unit" },
  { name: "Petard", category: "military", type: "unit" },
  { name: "Monk", category: "military", type: "unit" },

  // Ships
  { name: "Galley", category: "military", type: "unit" },
  { name: "Demolition Ship", category: "military", type: "unit" },
  { name: "Fire Ship", category: "military", type: "unit" },

  // Economy Units
  { name: "Villager", category: "economy", type: "unit" },
  { name: "Trade Cart", category: "economy", type: "unit" },
  { name: "Fishing Ship", category: "economy", type: "unit" },
  { name: "Transport Ship", category: "economy", type: "unit" },

  // Buildings
  { name: "Castle", category: "building", type: "building" },
  { name: "Town Center", category: "building", type: "building" },
  { name: "Barracks", category: "building", type: "building" },
  { name: "Archery Range", category: "building", type: "building" },
  { name: "Stable", category: "building", type: "building" },
  { name: "Siege Workshop", category: "building", type: "building" },
  { name: "Blacksmith", category: "building", type: "building" },
  { name: "Market", category: "building", type: "building" },
  { name: "Monastery", category: "building", type: "building" },
  { name: "University", category: "building", type: "building" },
  { name: "Watch Tower", category: "building", type: "building" },
  { name: "Dock", category: "building", type: "building" },
  { name: "House", category: "building", type: "building" },
  { name: "Mill", category: "building", type: "building" },
  { name: "Lumber Camp", category: "building", type: "building" },
  { name: "Mining Camp", category: "building", type: "building" },
  { name: "Farm", category: "building", type: "building" },
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
    civs,
  } = useCoachStore();

  const [activeFilter, setActiveFilter] = useState<
    "all" | "military" | "economy" | "building"
  >("all");
  const [db, setDb] = useState<AssetDatabase>({});
  const [hoveredEntity, setHoveredEntity] = useState<string | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });

  useEffect(() => {
    getAssetDatabase().then(setDb);
  }, []);

  // Check if opponent has unique units to dynamically inject into the grid
  const opponentCivMeta = civs.find(
    (c) => c.name.toLowerCase() === snapshot.opponent_civ.toLowerCase()
  );

  const dynamicEntities = [...TACTICAL_ENTITIES];
  if (opponentCivMeta && opponentCivMeta.unique_units) {
    opponentCivMeta.unique_units.forEach((uu) => {
      if (!dynamicEntities.some((e) => e.name.toLowerCase() === uu.toLowerCase())) {
        dynamicEntities.unshift({
          name: uu,
          category: "military",
          type: "unit",
        });
      }
    });
  }

  const filteredEntities = dynamicEntities.filter((e) => {
    if (activeFilter === "all") return true;
    return e.category === activeFilter;
  });

  const sightedUnitsList = Object.entries(snapshot.sighted_enemy_units);
  const sightedBldgsList = Object.entries(snapshot.sighted_enemy_buildings);
  const totalSightedCount =
    sightedUnitsList.reduce((acc, [, c]) => acc + c, 0) +
    sightedBldgsList.reduce((acc, [, c]) => acc + c, 0);

  const handleEntityClick = (entity: GridEntity) => {
    if (entity.type === "building") {
      addSightedBuilding(entity.name, 1);
    } else {
      addSightedUnit(entity.name, 1);
    }
  };

  const handleMouseMove = (e: React.MouseEvent, name: string) => {
    setHoveredEntity(name);
    setTooltipPos({ x: e.clientX + 12, y: e.clientY + 16 });
  };

  return (
    <section className="bg-surface-container parchment-panel p-5 sm:p-6 rounded-lg mb-8 border-outline shadow-sm">
      {/* Floating Tooltip */}
      {hoveredEntity && (
        <div
          className="fixed pointer-events-none z-50 bg-charcoal-ink text-on-primary px-2.5 py-1 rounded text-xs font-label-tactical shadow-lg border border-gold-leaf whitespace-nowrap"
          style={{ left: tooltipPos.x, top: tooltipPos.y }}
        >
          {hoveredEntity}
        </div>
      )}

      {/* Section Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gold-leaf text-on-primary flex items-center justify-center font-headline-md text-sm border border-surface-tint shrink-0">
            3
          </div>
          <h2 className="font-headline-lg text-lg sm:text-2xl text-primary uppercase tracking-wide font-bold">
            Fog of War: Tactical Grid
          </h2>
        </div>

        {totalSightedCount > 0 && (
          <button
            type="button"
            onClick={() => {
              clearSightedUnits();
              clearSightedBuildings();
            }}
            className="flex items-center gap-1.5 text-xs text-secondary hover:text-blood-accent bg-surface border border-outline-variant px-3 py-1.5 rounded transition-colors cursor-pointer font-label-tactical"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Sighted ({totalSightedCount})</span>
          </button>
        )}
      </div>

      {/* Observed Forces Container (Active Pill Tags) */}
      <div className="flex flex-wrap gap-2 mb-4 border-b border-outline-variant pb-4 min-h-[44px] items-center">
        {totalSightedCount === 0 ? (
          <p className="text-xs text-on-surface-variant italic font-body-md">
            No enemy units or structures sighted yet. Click icons below as you scout opponent forces.
          </p>
        ) : (
          <>
            {sightedUnitsList.map(([name, count]) => {
              const asset = getAssetFromCatalog(
                db,
                name,
                "unit",
                snapshot.opponent_civ
              );
              return (
                <button
                  key={name}
                  type="button"
                  onClick={() => removeSightedUnit(name, 1)}
                  title={`Click to remove 1 ${name}`}
                  className="observed-item bg-surface border border-secondary text-secondary px-3 py-1 rounded-full text-xs font-label-tactical flex items-center gap-2 shadow-sm relative cursor-pointer"
                >
                  {asset?.image ? (
                    <img
                      src={asset.image}
                      alt={name}
                      className="w-4 h-4 object-contain rounded-sm shrink-0"
                    />
                  ) : (
                    <span className="material-symbols-outlined text-[14px]">
                      sports_martial_arts
                    </span>
                  )}
                  <span className="font-bold">{name}</span>
                  <span className="badge bg-secondary text-on-secondary px-1.5 py-0.2 rounded-full text-[10px] font-bold">
                    {count}
                  </span>
                </button>
              );
            })}

            {sightedBldgsList.map(([name, count]) => {
              const asset = getAssetFromCatalog(
                db,
                name,
                "building",
                snapshot.opponent_civ
              );
              return (
                <button
                  key={name}
                  type="button"
                  onClick={() => removeSightedBuilding(name, 1)}
                  title={`Click to remove 1 ${name}`}
                  className="observed-item bg-surface border border-outline-variant text-on-surface-variant px-3 py-1 rounded-full text-xs font-label-tactical flex items-center gap-2 shadow-sm relative cursor-pointer opacity-90"
                >
                  {asset?.image ? (
                    <img
                      src={asset.image}
                      alt={name}
                      className="w-4 h-4 object-contain rounded-sm shrink-0"
                    />
                  ) : (
                    <span className="material-symbols-outlined text-[14px]">
                      account_balance
                    </span>
                  )}
                  <span className="font-bold">{name}</span>
                  <span className="badge bg-outline-variant text-on-surface px-1.5 py-0.2 rounded-full text-[10px] font-bold">
                    {count}
                  </span>
                </button>
              );
            })}
          </>
        )}
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-3">
        {(
          [
            { id: "all", label: "All" },
            { id: "military", label: "Military" },
            { id: "economy", label: "Economy" },
            { id: "building", label: "Buildings" },
          ] as const
        ).map((filter) => (
          <button
            key={filter.id}
            type="button"
            onClick={() => setActiveFilter(filter.id)}
            className={`px-3 py-1 rounded-full text-xs font-label-tactical transition-colors cursor-pointer ${
              activeFilter === filter.id
                ? "bg-outline text-on-primary font-bold shadow-sm"
                : "bg-surface border border-outline-variant text-on-surface-variant hover:bg-surface-variant"
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <p className="text-xs text-on-surface-variant mb-3 font-label-tactical">
        Click to spot opponent forces and structures.
      </p>

      {/* Grid of Tactical Unit & Building Icons */}
      <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12 gap-1.5 bg-surface-variant p-2.5 rounded border border-outline-variant">
        {filteredEntities.map((entity) => {
          const asset = getAssetFromCatalog(
            db,
            entity.name,
            entity.type,
            snapshot.opponent_civ
          );

          const count =
            entity.type === "building"
              ? snapshot.sighted_enemy_buildings[entity.name] || 0
              : snapshot.sighted_enemy_units[entity.name] || 0;

          const isSelected = count > 0;

          return (
            <button
              key={entity.name}
              type="button"
              onClick={() => handleEntityClick(entity)}
              onMouseEnter={(e) => handleMouseMove(e, entity.name)}
              onMouseMove={(e) => handleMouseMove(e, entity.name)}
              onMouseLeave={() => setHoveredEntity(null)}
              className={`tactical-unit-icon bg-surface border rounded flex items-center justify-center p-1 aspect-square relative cursor-pointer shadow-2xs ${
                isSelected
                  ? "border-gold-leaf ring-1 ring-gold-leaf bg-surface-container-high"
                  : "border-outline-variant hover:border-gold-leaf"
              }`}
            >
              {asset?.image ? (
                <img
                  src={asset.image}
                  alt={entity.name}
                  className="w-full h-full object-contain pointer-events-none"
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).style.display = "none";
                  }}
                />
              ) : (
                <span className="material-symbols-outlined text-outline text-lg pointer-events-none">
                  {entity.type === "building" ? "home" : "swords"}
                </span>
              )}

              {isSelected && (
                <span className="absolute -top-1.5 -right-1.5 bg-secondary text-on-secondary rounded-full text-[9px] font-bold px-1 font-label-tactical shadow-sm">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </section>
  );
};
