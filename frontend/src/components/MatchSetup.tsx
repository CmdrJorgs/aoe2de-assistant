"use client";

import React, { useState, useRef, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import { AgeNumber } from "@/types/coach";
import { getCivEmblemUrl, getAgeIconUrl } from "@/lib/assetDb";
import { User, Crosshair, Award, Clock, ChevronDown, Check, Search } from "lucide-react";

const AGES: { id: AgeNumber; name: string }[] = [
  { id: 1, name: "Dark Age" },
  { id: 2, name: "Feudal Age" },
  { id: 3, name: "Castle Age" },
  { id: 4, name: "Imperial Age" },
];

const DEFAULT_CIVS = [
  "Armenians",
  "Aztecs",
  "Bengalis",
  "Berbers",
  "Bohemians",
  "Britons",
  "Bulgarians",
  "Burgundians",
  "Burmese",
  "Byzantines",
  "Celts",
  "Chinese",
  "Cumans",
  "Dravidians",
  "Ethiopians",
  "Franks",
  "Georgians",
  "Goths",
  "Gurjaras",
  "Hindustanis",
  "Huns",
  "Incas",
  "Italians",
  "Japanese",
  "Khmer",
  "Koreans",
  "Lithuanians",
  "Magyars",
  "Malay",
  "Malians",
  "Mayans",
  "Mongols",
  "Persians",
  "Poles",
  "Portuguese",
  "Romans",
  "Saracens",
  "Sicilians",
  "Slavs",
  "Spanish",
  "Tatars",
  "Teutons",
  "Turks",
  "Vietnamese",
  "Vikings",
];

interface CivSelectProps {
  value: string;
  onChange: (civ: string) => void;
  civList: string[];
  label: string;
  icon: React.ReactNode;
}

const CivSelect: React.FC<CivSelectProps> = ({
  value,
  onChange,
  civList,
  label,
  icon,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchQuery("");
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
        setSearchQuery("");
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
      // Auto-focus search input when opened
      setTimeout(() => searchInputRef.current?.focus(), 50);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  const filteredCivs = civList.filter((civ) =>
    civ.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const emblemUrl = getCivEmblemUrl(value);

  return (
    <div className="space-y-2 relative" ref={dropdownRef}>
      <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
        {icon}
        <span>{label}</span>
      </label>

      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full input-sunken bg-surface flex items-center justify-between gap-2 px-3 py-2 rounded h-11 border border-outline-variant hover:border-gold-leaf/60 transition-colors cursor-pointer text-left"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          <img
            src={emblemUrl}
            alt={value}
            className="w-6 h-6 object-contain rounded-xs shrink-0 border border-outline-variant bg-surface-variant"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).src =
                "/aoe2_assets/icons/age-3.png";
            }}
          />
          <span className="font-body-md text-sm text-primary font-medium truncate">
            {value}
          </span>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-on-surface-variant shrink-0 transition-transform duration-200 ${
            isOpen ? "rotate-180 text-gold-leaf" : ""
          }`}
        />
      </button>

      {/* Custom Dropdown Menu */}
      {isOpen && (
        <div
          style={{ position: "absolute" }}
          className="top-full left-0 right-0 mt-1.5 z-20 bg-surface-container border border-outline-variant rounded-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-100"
        >
          {/* Search Bar */}
          <div className="p-2 border-b border-outline-variant bg-surface-variant/40 flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-on-surface-variant shrink-0" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Filter civ..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-surface border border-outline-variant rounded px-2 py-1 text-xs text-primary placeholder:text-on-surface-variant/60 focus:outline-none focus:border-gold-leaf"
            />
          </div>

          {/* Civ Options List */}
          <div className="max-h-60 overflow-y-auto p-1 space-y-0.5 custom-scrollbar">
            {filteredCivs.length === 0 ? (
              <div className="py-3 px-2 text-center text-xs text-on-surface-variant italic">
                No civilization found
              </div>
            ) : (
              filteredCivs.map((civ) => {
                const isSelected = civ.toLowerCase() === value.toLowerCase();
                const civEmblem = getCivEmblemUrl(civ);

                return (
                  <button
                    key={civ}
                    type="button"
                    onClick={() => {
                      onChange(civ);
                      setIsOpen(false);
                      setSearchQuery("");
                    }}
                    className={`w-full flex items-center justify-between gap-2.5 px-2.5 py-1.5 rounded text-left transition-colors cursor-pointer ${
                      isSelected
                        ? "bg-parchment-deep text-primary font-bold border border-gold-leaf/50"
                        : "text-on-surface hover:bg-surface-variant hover:text-primary"
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                      <img
                        src={civEmblem}
                        alt={civ}
                        className="w-5 h-5 object-contain rounded-xs shrink-0 border border-outline-variant/40 bg-surface-variant"
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).src =
                            "/aoe2_assets/icons/age-3.png";
                        }}
                      />
                      <span className="font-body-md text-xs sm:text-sm truncate">
                        {civ}
                      </span>
                    </div>
                    {isSelected && (
                      <Check className="w-3.5 h-3.5 text-gold-leaf shrink-0" />
                    )}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export const MatchSetup: React.FC = () => {
  const { snapshot, updateSnapshot, civs } = useCoachStore();

  const eloScrollRef = useRef<HTMLDivElement>(null);
  const timeScrollRef = useRef<HTMLDivElement>(null);

  const civList =
    civs.length > 0
      ? civs.map((c) => c.name).sort((a, b) => a.localeCompare(b))
      : DEFAULT_CIVS.sort((a, b) => a.localeCompare(b));

  const handleCivChange = (type: "player" | "opponent", civName: string) => {
    if (type === "player") updateSnapshot({ player_civ: civName });
    else updateSnapshot({ opponent_civ: civName });
  };

  const handlePlayerAgeChange = (age: AgeNumber) => {
    updateSnapshot({ current_age: age });
  };

  const handleOpponentAgeChange = (age: AgeNumber) => {
    updateSnapshot({ opponent_estimated_age: age });
  };

  const handleEloChange = (elo: number) => {
    updateSnapshot({
      player_elo: Math.max(0, Math.min(3000, Math.round(elo / 50) * 50)),
    });
  };

  // Scroll wheel support on Your ELO badge/number
  useEffect(() => {
    const el = eloScrollRef.current;
    if (!el) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 50 : -50;
      updateSnapshot({
        player_elo: Math.max(0, Math.min(3000, snapshot.player_elo + delta)),
      });
    };

    el.addEventListener("wheel", handleWheel, { passive: false });
    return () => el.removeEventListener("wheel", handleWheel);
  }, [snapshot.player_elo, updateSnapshot]);

  // Scroll wheel support on Game Time badge/number
  useEffect(() => {
    const el = timeScrollRef.current;
    if (!el) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 1 : -1;
      updateSnapshot({
        game_time_minutes: Math.max(0, snapshot.game_time_minutes + delta),
      });
    };

    el.addEventListener("wheel", handleWheel, { passive: false });
    return () => el.removeEventListener("wheel", handleWheel);
  }, [snapshot.game_time_minutes, updateSnapshot]);

  const minutes = Math.floor(snapshot.game_time_minutes);
  const seconds = Math.round((snapshot.game_time_minutes % 1) * 60);
  const formattedTime = `${minutes}:${String(seconds).padStart(2, "0")}`;

  const opponentAge = snapshot.opponent_estimated_age ?? snapshot.current_age;

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
        <CivSelect
          value={snapshot.player_civ}
          onChange={(civ) => handleCivChange("player", civ)}
          civList={civList}
          label="Your Civilization"
          icon={<User className="w-3.5 h-3.5 text-gold-leaf" />}
        />

        {/* 2. Opponent Civilization */}
        <CivSelect
          value={snapshot.opponent_civ}
          onChange={(civ) => handleCivChange("opponent", civ)}
          civList={civList}
          label="Opponent Civilization"
          icon={<Crosshair className="w-3.5 h-3.5 text-secondary" />}
        />

        {/* 3. Your ELO (Slider 0-3000 in increments of 50 + Wheel Scroll) */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
              <Award className="w-3.5 h-3.5 text-gold-leaf" />
              <span>Your ELO</span>
            </label>
            <div
              ref={eloScrollRef}
              title="Hover & scroll mouse wheel to adjust ELO (+/- 50)"
              className="font-label-tactical text-gold-leaf font-bold text-xs bg-surface-variant px-2 py-0.5 rounded border border-outline-variant hover:border-gold-leaf hover:bg-parchment-deep cursor-ns-resize transition-all select-none flex items-center gap-1 shadow-xs"
            >
              <span>{snapshot.player_elo}</span>
              <span className="text-[10px] text-on-surface-variant font-normal">ELO</span>
            </div>
          </div>
          <div className="flex flex-col justify-center h-11 px-3 input-sunken bg-surface rounded">
            <input
              type="range"
              min={0}
              max={3000}
              step={50}
              value={snapshot.player_elo}
              onChange={(e) => handleEloChange(parseInt(e.target.value) || 0)}
              className="w-full accent-gold-leaf h-2 bg-outline-variant rounded-full appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-label-tactical text-on-surface-variant mt-1 select-none">
              <span>0</span>
              <span>1500</span>
              <span>3000</span>
            </div>
          </div>
        </div>

        {/* 4. Game Time (Four Buttons -5m, -1m, +1m, +5m + Wheel Scroll) */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
              <Clock className="w-3.5 h-3.5 text-tertiary" />
              <span>Game Time</span>
            </label>
            <div
              ref={timeScrollRef}
              title="Hover & scroll mouse wheel to adjust Game Time (+/- 1m)"
              className="font-label-tactical text-tertiary font-bold text-xs bg-surface-variant px-2 py-0.5 rounded border border-outline-variant hover:border-tertiary hover:bg-parchment-deep cursor-ns-resize transition-all select-none shadow-xs"
            >
              {formattedTime}
            </div>
          </div>
          <div className="flex items-center gap-1.5 h-11">
            <button
              type="button"
              onClick={() =>
                updateSnapshot({
                  game_time_minutes: Math.max(0, snapshot.game_time_minutes - 5),
                })
              }
              className="flex-1 bg-surface-variant text-on-surface hover:bg-outline-variant active:scale-95 border border-outline-variant text-xs py-2 px-1 rounded font-label-tactical font-bold transition-all text-center cursor-pointer"
              title="Subtract 5 minutes"
            >
              -5m
            </button>
            <button
              type="button"
              onClick={() =>
                updateSnapshot({
                  game_time_minutes: Math.max(0, snapshot.game_time_minutes - 1),
                })
              }
              className="flex-1 bg-surface-variant text-on-surface hover:bg-outline-variant active:scale-95 border border-outline-variant text-xs py-2 px-1 rounded font-label-tactical font-bold transition-all text-center cursor-pointer"
              title="Subtract 1 minute"
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
              className="flex-1 bg-surface-variant text-on-surface hover:bg-outline-variant active:scale-95 border border-outline-variant text-xs py-2 px-1 rounded font-label-tactical font-bold transition-all text-center cursor-pointer"
              title="Add 1 minute"
            >
              +1m
            </button>
            <button
              type="button"
              onClick={() =>
                updateSnapshot({
                  game_time_minutes: snapshot.game_time_minutes + 5,
                })
              }
              className="flex-1 bg-surface-variant text-on-surface hover:bg-outline-variant active:scale-95 border border-outline-variant text-xs py-2 px-1 rounded font-label-tactical font-bold transition-all text-center cursor-pointer"
              title="Add 5 minutes"
            >
              +5m
            </button>
          </div>
        </div>
      </div>

      <div className="hr-decorative mb-5"></div>

      {/* Age Rows: Your Age & Opponent Age */}
      <div className="space-y-4">
        {/* 1. Your Age */}
        <div className="space-y-2">
          <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
            <User className="w-3.5 h-3.5 text-gold-leaf" />
            <span>Your Age</span>
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 w-full rounded-lg overflow-hidden border border-outline-variant shadow-sm bg-surface p-1.5">
            {AGES.map((age) => {
              const isSelected = snapshot.current_age === age.id;
              const ageIcon = getAgeIconUrl(age.id);

              return (
                <button
                  key={`your-age-${age.id}`}
                  type="button"
                  onClick={() => handlePlayerAgeChange(age.id)}
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

        {/* 2. Opponent Age */}
        <div className="space-y-2">
          <label className="flex items-center gap-1.5 font-label-tactical text-xs text-on-surface font-semibold">
            <Crosshair className="w-3.5 h-3.5 text-secondary" />
            <span>Opponent Age</span>
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 w-full rounded-lg overflow-hidden border border-outline-variant shadow-sm bg-surface p-1.5">
            {AGES.map((age) => {
              const isSelected = opponentAge === age.id;
              const ageIcon = getAgeIconUrl(age.id);

              return (
                <button
                  key={`opponent-age-${age.id}`}
                  type="button"
                  onClick={() => handleOpponentAgeChange(age.id)}
                  className={`py-2.5 px-3 flex items-center justify-center gap-2.5 font-body-md text-xs sm:text-sm rounded transition-all cursor-pointer ${
                    isSelected
                      ? "bg-parchment-deep text-primary font-bold border border-secondary shadow-sm"
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
      </div>
    </section>
  );
};
