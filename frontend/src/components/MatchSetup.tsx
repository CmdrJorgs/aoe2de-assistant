"use client";

import React from "react";
import { useCoachStore } from "@/lib/store";
import { AgeNumber } from "@/types/coach";
import { getCivEmblemUrl, getAgeIconUrl } from "@/lib/assetDb";
import { User, Crosshair, Award, Clock, Shield } from "lucide-react";

const AGES: { id: AgeNumber; name: string }[] = [
  { id: 1, name: "Dark Age" },
  { id: 2, name: "Feudal Age" },
  { id: 3, name: "Castle Age" },
  { id: 4, name: "Imperial Age" },
];

const DEFAULT_CIVS = [
  "Franks",
  "Vikings",
  "Britons",
  "Goths",
  "Teutons",
  "Mongols",
  "Mayans",
  "Aztecs",
  "Chinese",
  "Japanese",
  "Byzantines",
  "Huns",
  "Spanish",
  "Saracens",
  "Turks",
  "Persians",
  "Celts",
  "Italians",
  "Magyars",
  "Berbers",
  "Ethiopians",
  "Malians",
  "Portuguese",
  "Burmese",
  "Khmer",
  "Malay",
  "Vietnamese",
  "Bulgarians",
  "Cumans",
  "Lithuanians",
  "Tatars",
  "Burgundians",
  "Sicilians",
  "Bohemians",
  "Poles",
  "Bengalis",
  "Dravidians",
  "Gurjaras",
  "Hindustanis",
  "Romans",
  "Armenians",
  "Georgians",
];

export const MatchSetup: React.FC = () => {
  const { snapshot, updateSnapshot, civs } = useCoachStore();

  const civList =
    civs.length > 0
      ? civs.map((c) => c.name).sort((a, b) => a.localeCompare(b))
      : DEFAULT_CIVS.sort((a, b) => a.localeCompare(b));

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

  const minutes = Math.floor(snapshot.game_time_minutes);
  const seconds = Math.round((snapshot.game_time_minutes % 1) * 60);
  const formattedTime = `${minutes}:${String(seconds).padStart(2, "0")}`;

  const playerEmblem = getCivEmblemUrl(snapshot.player_civ);
  const opponentEmblem = getCivEmblemUrl(snapshot.opponent_civ);

  return (
    <section className="bg-surface-container parchment-panel p-5 sm:p-6 rounded-lg">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gold-leaf text-on-primary flex items-center justify-center font-headline-md text-sm border border-surface-tint shrink-0">
            1
          </div>
          <h2 className="font-headline-lg text-lg sm:text-2xl text-primary uppercase tracking-wide font-bold">
            Match Context & Setup
          </h2>
        </div>
        <div className="font-label-tactical text-xs sm:text-sm text-on-surface-variant bg-surface-variant px-3 py-1 border border-outline-variant rounded">
          {snapshot.player_civ} vs {snapshot.opponent_civ}
        </div>
      </div>

      {/* Grid Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6 mb-6">
        {/* 1. Your Civilization */}
        <div className="space-y-2">
          <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
            <User className="w-3.5 h-3.5 text-gold-leaf" />
            <span>Your Civilization</span>
          </label>
          <div className="input-sunken bg-surface flex items-center gap-2 px-3 py-2 rounded h-11">
            <img
              src={playerEmblem}
              alt={snapshot.player_civ}
              className="w-6 h-6 object-contain rounded-sm shrink-0 border border-outline-variant bg-surface-variant"
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).src =
                  "/aoe2_assets/icons/age-3.png";
              }}
            />
            <select
              value={snapshot.player_civ}
              onChange={(e) => handleCivChange("player", e.target.value)}
              className="flex-1 bg-transparent text-primary font-body-md text-sm focus:outline-none cursor-pointer"
            >
              {civList.map((c) => (
                <option key={c} value={c} className="bg-surface text-primary">
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 2. Opponent Civilization */}
        <div className="space-y-2">
          <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
            <Crosshair className="w-3.5 h-3.5 text-secondary" />
            <span>Opponent Civilization</span>
          </label>
          <div className="input-sunken bg-surface flex items-center gap-2 px-3 py-2 rounded h-11">
            <img
              src={opponentEmblem}
              alt={snapshot.opponent_civ}
              className="w-6 h-6 object-contain rounded-sm shrink-0 border border-outline-variant bg-surface-variant"
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).src =
                  "/aoe2_assets/icons/age-3.png";
              }}
            />
            <select
              value={snapshot.opponent_civ}
              onChange={(e) => handleCivChange("opponent", e.target.value)}
              className="flex-1 bg-transparent text-primary font-body-md text-sm focus:outline-none cursor-pointer"
            >
              {civList.map((c) => (
                <option key={c} value={c} className="bg-surface text-primary">
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 3. Player ELO */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
              <Award className="w-3.5 h-3.5 text-gold-leaf" />
              <span>Player ELO</span>
            </label>
            <span className="font-label-tactical text-gold-leaf font-bold text-xs">
              {snapshot.player_elo}
            </span>
          </div>
          <div className="flex gap-1.5 h-11">
            <input
              type="number"
              min={400}
              max={3000}
              step={25}
              value={snapshot.player_elo}
              onChange={(e) => handleEloChange(parseInt(e.target.value) || 1000)}
              className="input-sunken bg-surface px-3 py-2 rounded flex-1 font-label-tactical text-sm text-primary font-bold text-center focus:outline-none"
            />
            <div className="flex gap-1">
              {[800, 1200, 1600].map((elo) => (
                <button
                  key={elo}
                  type="button"
                  onClick={() => handleEloChange(elo)}
                  className={`px-2 py-1 text-[11px] font-label-tactical rounded border transition-colors ${
                    snapshot.player_elo === elo
                      ? "bg-gold-leaf text-on-primary border-gold-leaf font-bold"
                      : "bg-surface-variant text-on-surface-variant border-outline-variant hover:bg-outline-variant"
                  }`}
                >
                  {elo}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 4. Game Time */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
              <Clock className="w-3.5 h-3.5 text-tertiary" />
              <span>Game Time</span>
            </label>
            <span className="font-label-tactical text-tertiary font-bold text-xs">
              {formattedTime}
            </span>
          </div>
          <div className="flex items-center gap-2 h-11">
            <input
              type="range"
              min={1}
              max={60}
              step={0.5}
              value={snapshot.game_time_minutes}
              onChange={(e) =>
                updateSnapshot({ game_time_minutes: parseFloat(e.target.value) })
              }
              className="w-full accent-tertiary h-2 bg-outline-variant rounded-full appearance-none cursor-pointer"
            />
            <button
              type="button"
              onClick={() =>
                updateSnapshot({
                  game_time_minutes: Math.max(1, snapshot.game_time_minutes - 1),
                })
              }
              className="bg-surface-variant text-on-surface-variant border border-outline-variant text-xs px-2 py-1.5 rounded-sm hover:bg-outline-variant cursor-pointer shrink-0 font-label-tactical"
            >
              -1m
            </button>
            <button
              type="button"
              onClick={() =>
                updateSnapshot({
                  game_time_minutes: snapshot.game_time_minutes + 1,
                })
              }
              className="bg-surface-variant text-on-surface-variant border border-outline-variant text-xs px-2 py-1.5 rounded-sm hover:bg-outline-variant cursor-pointer shrink-0 font-label-tactical"
            >
              +1m
            </button>
          </div>
        </div>
      </div>

      <div className="hr-decorative mb-5"></div>

      {/* Current Game Age */}
      <div className="space-y-2.5">
        <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
          <Shield className="w-3.5 h-3.5 text-primary" />
          <span>Current Game Age</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 w-full rounded-lg overflow-hidden border border-outline-variant shadow-sm bg-surface p-1.5">
          {AGES.map((age) => {
            const isSelected = snapshot.current_age === age.id;
            const ageIcon = getAgeIconUrl(age.id);

            return (
              <button
                key={age.id}
                type="button"
                onClick={() => handleAgeChange(age.id)}
                className={`py-2.5 px-3 flex items-center justify-center gap-2.5 font-body-md text-xs sm:text-sm rounded transition-all cursor-pointer ${
                  isSelected
                    ? "bg-parchment-deep text-primary font-bold border border-gold-leaf shadow-sm"
                    : "bg-surface text-on-surface-variant hover:bg-surface-variant border border-transparent"
                }`}
              >
                <img
                  src={ageIcon}
                  alt={age.name}
                  className="w-5 h-5 sm:w-6 sm:h-6 object-contain shrink-0"
                />
                <span className="truncate">{age.name}</span>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
};
