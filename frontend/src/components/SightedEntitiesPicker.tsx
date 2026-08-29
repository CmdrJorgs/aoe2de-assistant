"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useCoachStore } from "@/lib/store";
import {
  getAssetDatabase,
  getAssetFromCatalog,
  getCivEntities,
  AssetDatabase,
  CivGridEntity,
} from "@/lib/assetDb";
import { Trash2 } from "lucide-react";

// Fallback tactical entities before database loads
const FALLBACK_ENTITIES: CivGridEntity[] = [
  { name: "Militia", category: "military", type: "unit", image: "/aoe2_assets/units/008_militia.png" },
  { name: "Spearman", category: "military", type: "unit", image: "/aoe2_assets/units/031_spearman.png" },
  { name: "Eagle Scout", category: "military", type: "unit", image: "/aoe2_assets/units/040_eagle_scout.png" },
  { name: "Archer", category: "military", type: "unit", image: "/aoe2_assets/units/017_archer.png" },
  { name: "Skirmisher", category: "military", type: "unit", image: "/aoe2_assets/units/020_skirmisher.png" },
  { name: "Cavalry Archer", category: "military", type: "unit", image: "/aoe2_assets/units/019_cavalry_archer.png" },
  { name: "Scout Cavalry", category: "military", type: "unit", image: "/aoe2_assets/units/000_scout_cavalry.png" },
  { name: "Knight", category: "military", type: "unit", image: "/aoe2_assets/units/001_knight.png" },
  { name: "Camel", category: "military", type: "unit", image: "/aoe2_assets/units/002_camel.png" },
  { name: "Battering Ram", category: "military", type: "unit", image: "/aoe2_assets/units/024_battering_ram.png" },
  { name: "Mangonel", category: "military", type: "unit", image: "/aoe2_assets/units/025_mangonel.png" },
  { name: "Scorpion", category: "military", type: "unit", image: "/aoe2_assets/units/026_scorpion.png" },
  { name: "Trebuchet", category: "military", type: "unit", image: "/aoe2_assets/units/028_trebuchet.png" },
  { name: "Petard", category: "military", type: "unit", image: "/aoe2_assets/units/027_petard.png" },
  { name: "Monk", category: "military", type: "unit", image: "/aoe2_assets/units/030_monk.png" },
  { name: "Galley", category: "military", type: "unit", image: "/aoe2_assets/units/033_galley.png" },
  { name: "Demolition Ship", category: "military", type: "unit", image: "/aoe2_assets/units/035_demolition_ship.png" },
  { name: "Fire Ship", category: "military", type: "unit", image: "/aoe2_assets/units/036_fire_ship.png" },
  { name: "Villager", category: "economy", type: "unit", image: "/aoe2_assets/units/083_villager.png" },
  { name: "Trade Cart", category: "economy", type: "unit", image: "/aoe2_assets/units/128_trade_cart.png" },
  { name: "Fishing Ship", category: "economy", type: "unit", image: "/aoe2_assets/units/013_fishing_ship.png" },
  { name: "Transport Ship", category: "economy", type: "unit", image: "/aoe2_assets/units/545_transport_ship.png" },
  { name: "Castle", category: "building", type: "building", image: "/aoe2_assets/buildings/015_castle.png" },
  { name: "Town Center", category: "building", type: "building", image: "/aoe2_assets/buildings/014_town_center.png" },
  { name: "Barracks", category: "building", type: "building", image: "/aoe2_assets/buildings/002_barracks_1.png" },
  { name: "Archery Range", category: "building", type: "building", image: "/aoe2_assets/buildings/000_archery_range_1.png" },
  { name: "Stable", category: "building", type: "building", image: "/aoe2_assets/buildings/023_stable_1.png" },
  { name: "Siege Workshop", category: "building", type: "building", image: "/aoe2_assets/buildings/022_siege_workshop_2.png" },
  { name: "Blacksmith", category: "building", type: "building", image: "/aoe2_assets/buildings/004_blacksmith_1.png" },
  { name: "Market", category: "building", type: "building", image: "/aoe2_assets/buildings/018_market.png" },
  { name: "Monastery", category: "building", type: "building", image: "/aoe2_assets/buildings/019_monastery.png" },
  { name: "University", category: "building", type: "building", image: "/aoe2_assets/buildings/033_university.png" },
  { name: "Watch Tower", category: "building", type: "building", image: "/aoe2_assets/buildings/025_tower.png" },
  { name: "Dock", category: "building", type: "building", image: "/aoe2_assets/buildings/013_dock_1.png" },
  { name: "House", category: "building", type: "building", image: "/aoe2_assets/buildings/017_house_1.png" },
  { name: "Mill", category: "building", type: "building", image: "/aoe2_assets/buildings/020_mill_1.png" },
  { name: "Lumber Camp", category: "building", type: "building", image: "/aoe2_assets/buildings/016_lumber_camp_1.png" },
  { name: "Mining Camp", category: "building", type: "building", image: "/aoe2_assets/buildings/021_mining_camp_1.png" },
  { name: "Farm", category: "building", type: "building", image: "/aoe2_assets/buildings/006_farm_1.png" },
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

  // Fetch possible enemy units and buildings dynamically for the selected opponent civ
  const opponentCivEntities = useMemo(() => {
    const fetched = getCivEntities(db, snapshot.opponent_civ);
    const baseList = fetched.length > 0 ? fetched : FALLBACK_ENTITIES;

    // Check if opponent metadata has unique units to guarantee inclusion
    const opponentCivMeta = civs.find(
      (c) => c.name.toLowerCase() === snapshot.opponent_civ.toLowerCase()
    );

    const result = [...baseList];
    if (opponentCivMeta && opponentCivMeta.unique_units) {
      opponentCivMeta.unique_units.forEach((uu) => {
        if (!result.some((e) => e.name.toLowerCase() === uu.toLowerCase())) {
          const asset = getAssetFromCatalog(db, uu, "unit", snapshot.opponent_civ);
          result.unshift({
            name: uu,
            category: "military",
            type: "unit",
            image: asset?.image || "",
          });
        }
      });
    }

    return result;
  }, [db, snapshot.opponent_civ, civs]);

  const filteredEntities = useMemo(() => {
    if (activeFilter === "all") return opponentCivEntities;
    return opponentCivEntities.filter((e) => e.category === activeFilter);
  }, [opponentCivEntities, activeFilter]);

  const sightedUnitsList = Object.entries(snapshot.sighted_enemy_units);
  const sightedBldgsList = Object.entries(snapshot.sighted_enemy_buildings);
  const totalSightedCount =
    sightedUnitsList.reduce((acc, [, c]) => acc + c, 0) +
    sightedBldgsList.reduce((acc, [, c]) => acc + c, 0);

  const handleEntityClick = (entity: CivGridEntity) => {
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
          const imgUrl =
            entity.image ||
            getAssetFromCatalog(
              db,
              entity.name,
              entity.type,
              snapshot.opponent_civ
            )?.image;

          const count =
            entity.type === "building"
              ? snapshot.sighted_enemy_buildings[entity.name] || 0
              : snapshot.sighted_enemy_units[entity.name] || 0;

          const isSelected = count > 0;

          return (
            <button
              key={`${entity.type}-${entity.name}`}
              type="button"
              onClick={() => handleEntityClick(entity)}
              onMouseEnter={(e) => handleMouseMove(e, entity.name)}
              onMouseMove={(e) => handleMouseMove(e, entity.name)}
              onMouseLeave={() => setHoveredEntity(null)}
              title={entity.name}
              aria-label={`${entity.name}${count > 0 ? ` (${count} sighted)` : ""}`}
              className={`tactical-unit-icon bg-surface border rounded flex items-center justify-center p-0 aspect-square relative cursor-pointer shadow-2xs overflow-hidden ${
                isSelected
                  ? "border-gold-leaf ring-2 ring-gold-leaf bg-surface-container-high"
                  : "border-outline-variant hover:border-gold-leaf"
              }`}
            >
              {imgUrl ? (
                <img
                  src={imgUrl}
                  alt={entity.name}
                  className="w-full h-full object-cover block pointer-events-none"
                  loading="lazy"
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
                <span className="absolute top-0.5 right-0.5 bg-secondary text-on-secondary rounded-full text-[9px] font-bold px-1 font-label-tactical shadow-sm pointer-events-none z-10 leading-tight">
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
