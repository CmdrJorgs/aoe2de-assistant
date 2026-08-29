"use client";

import React from "react";
import { useCoachStore } from "@/lib/store";
import {
  Mic,
  RotateCcw,
  Sparkles,
  BookOpen,
  HelpCircle,
} from "lucide-react";

interface HeaderProps {
  onOpenVoice: () => void;
  activeNav?: string;
  onSelectNav?: (nav: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenVoice,
  activeNav = "war-room",
  onSelectNav,
}) => {
  const {
    presets,
    applyPreset,
    selectedPresetId,
    resetSnapshot,
    health,
  } = useCoachStore();

  return (
    <header className="bg-parchment-deep text-primary border-b border-outline-variant shadow-sm flex justify-between items-center w-full px-4 sm:px-6 py-3.5 sticky top-0 z-30">
      {/* Left Area: Mobile Title / Desktop Navigation Links */}
      <div className="flex items-center gap-4 sm:gap-6">
        <div className="font-headline-lg text-xl sm:text-2xl font-bold text-gold-leaf md:hidden">
          AoE2 Coach AI
        </div>

        <nav className="hidden md:flex gap-5 lg:gap-6 items-center">
          <button
            type="button"
            onClick={() => onSelectNav?.("war-room")}
            className={`pb-1 font-headline-md text-base sm:text-lg transition-all duration-200 cursor-pointer ${
              activeNav === "war-room"
                ? "text-secondary border-b-2 border-gold-leaf font-bold"
                : "text-on-surface-variant hover:text-blood-accent"
            }`}
          >
            War Room
          </button>

          <button
            type="button"
            onClick={() => onSelectNav?.("history")}
            className={`font-headline-md text-base sm:text-lg transition-all duration-200 cursor-pointer ${
              activeNav === "history"
                ? "text-secondary border-b-2 border-gold-leaf font-bold"
                : "text-on-surface-variant hover:text-blood-accent"
            }`}
          >
            History
          </button>

          <button
            type="button"
            onClick={() => onSelectNav?.("tactics")}
            className={`font-headline-md text-base sm:text-lg transition-all duration-200 cursor-pointer ${
              activeNav === "tactics"
                ? "text-secondary border-b-2 border-gold-leaf font-bold"
                : "text-on-surface-variant hover:text-blood-accent"
            }`}
          >
            Tactics
          </button>

          <div className="w-px h-5 bg-outline-variant mx-1"></div>

          <button
            type="button"
            onClick={() => onSelectNav?.("codex")}
            className="text-on-surface-variant font-headline-md text-base hover:text-blood-accent transition-colors duration-200 flex items-center gap-1.5 cursor-pointer"
          >
            <BookOpen className="w-4 h-4 text-gold-leaf" />
            <span>Codex</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectNav?.("support")}
            className="text-on-surface-variant font-headline-md text-base hover:text-blood-accent transition-colors duration-200 flex items-center gap-1.5 cursor-pointer"
          >
            <HelpCircle className="w-4 h-4 text-gold-leaf" />
            <span>Support</span>
          </button>
        </nav>
      </div>

      {/* Right Area: Presets, Voice, Action Buttons & Profile */}
      <div className="flex items-center gap-2 sm:gap-3 text-on-surface-variant">
        {/* Preset Selector */}
        {presets && presets.length > 0 && (
          <div className="hidden sm:flex items-center gap-1.5 bg-surface border border-outline-variant rounded px-2.5 py-1 text-xs font-label-tactical">
            <Sparkles className="w-3.5 h-3.5 text-gold-leaf shrink-0" />
            <select
              value={selectedPresetId || ""}
              onChange={(e) => {
                const p = presets.find((x) => x.id === e.target.value);
                if (p) applyPreset(p);
              }}
              className="bg-transparent text-primary focus:outline-none cursor-pointer text-xs"
            >
              <option value="" disabled>
                Load Scenario...
              </option>
              {presets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title} ({p.difficulty})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Voice Trigger Button */}
        <button
          type="button"
          onClick={onOpenVoice}
          title="Voice Tactical Input"
          className="flex items-center gap-1.5 bg-surface hover:bg-surface-variant border border-outline-variant px-2.5 py-1.5 rounded text-xs font-label-tactical text-primary transition-colors cursor-pointer shadow-sm"
        >
          <Mic className="w-3.5 h-3.5 text-gold-leaf" />
          <span className="hidden sm:inline font-bold">Voice Update</span>
        </button>

        {/* Reset Button */}
        <button
          type="button"
          onClick={resetSnapshot}
          title="Reset Match State"
          className="hover:text-blood-accent transition-colors duration-200 p-1.5 rounded hover:bg-surface-variant cursor-pointer"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        {/* Engine Status Dot */}
        <div
          title={health?.status === "healthy" ? "AI Engine Connected" : "Connecting..."}
          className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-label-tactical border border-outline-variant bg-surface"
        >
          <div
            className={`w-2 h-2 rounded-full ${
              health?.status === "healthy" ? "bg-tertiary" : "bg-gold-leaf animate-pulse"
            }`}
          />
          <span className="hidden lg:inline text-xs text-on-surface-variant">
            {health?.status === "healthy" ? "Engine Ready" : "Standby"}
          </span>
        </div>

        {/* Profile Avatar / Tactical Insignia */}
        <div className="flex items-center ml-1">
          <img
            alt="Royal Tactician Profile"
            className="w-8 h-8 sm:w-9 sm:h-9 rounded-full border-2 border-gold-leaf object-cover shadow-sm bg-surface"
            src="/aoe2_assets/icons/shield_imperial-age_active.png"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).src =
                "/aoe2_assets/icons/age-4.png";
            }}
          />
        </div>
      </div>
    </header>
  );
};
