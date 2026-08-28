/**
 * Zustand Store for AoE2 Coach Web Application
 */

import { create } from "zustand";
import {
  SnapshotInput,
  RecommendationResponse,
  PresetScenario,
  CivMetadata,
  UnitMetadata,
  HealthResponse,
} from "@/types/coach";
import { api } from "@/lib/api";

const DEFAULT_SNAPSHOT: SnapshotInput = {
  player_civ: "Franks",
  opponent_civ: "Vikings",
  player_elo: 1000,
  game_time_minutes: 20.0,
  current_age: 3,
  food: 320,
  wood: 750,
  gold: 120,
  stone: 450,
  vills_food: 14,
  vills_wood: 26,
  vills_gold: 6,
  vills_stone: 2,
  military_units: { "Scout Cavalry": 4, "Knight": 2 },
  player_buildings: { "Town Center": 2, "Barracks": 1, "Stable": 1, "Blacksmith": 1 },
  completed_techs: ["Wheelbarrow", "Double-Bit Axe", "Horse Collar"],
  sighted_enemy_units: { "Berserk": 5 },
  sighted_enemy_buildings: { "Castle": 1 },
  user_notes: "",
  force_fallback: false,
};

interface CoachStore {
  // Snapshot State
  snapshot: SnapshotInput;
  setSnapshot: (snapshot: SnapshotInput) => void;
  updateSnapshot: (partial: Partial<SnapshotInput>) => void;
  resetSnapshot: () => void;
  
  // Sighted Entities helpers
  addSightedUnit: (unitName: string, count?: number) => void;
  removeSightedUnit: (unitName: string, count?: number) => void;
  setSightedUnitCount: (unitName: string, count: number) => void;
  clearSightedUnits: () => void;
  
  addSightedBuilding: (bldgName: string, count?: number) => void;
  removeSightedBuilding: (bldgName: string, count?: number) => void;
  setSightedBuildingCount: (bldgName: string, count: number) => void;
  clearSightedBuildings: () => void;

  // Metadata Cache
  civs: CivMetadata[];
  units: UnitMetadata[];
  presets: PresetScenario[];
  selectedPresetId: string | null;
  loadMetadata: () => Promise<void>;
  applyPreset: (preset: PresetScenario) => void;

  // Recommendation & Inference State
  recommendation: RecommendationResponse | null;
  isLoading: boolean;
  error: string | null;
  getTacticalRecommendation: () => Promise<void>;
  
  // Checklist tracker (persisted checkboxes)
  completedChecklistItems: Record<string, boolean>;
  toggleChecklistItem: (item: string) => void;

  // Voice State
  isListening: boolean;
  voiceTranscript: string;
  voiceConfidence: number;
  voiceFeedback: string | null;
  setIsListening: (val: boolean) => void;
  setVoiceTranscript: (transcript: string) => void;
  applyVoiceTranscript: (transcript: string) => Promise<void>;

  // Health / Connection State
  health: HealthResponse | null;
  checkHealth: () => Promise<void>;
}

export const useCoachStore = create<CoachStore>((set, get) => ({
  snapshot: DEFAULT_SNAPSHOT,
  setSnapshot: (snapshot) => set({ snapshot }),
  updateSnapshot: (partial) =>
    set((state) => ({
      snapshot: { ...state.snapshot, ...partial },
    })),
  resetSnapshot: () => set({ snapshot: DEFAULT_SNAPSHOT, recommendation: null }),

  // Sighted Units
  addSightedUnit: (unitName, count = 1) => {
    set((state) => {
      const cur = { ...state.snapshot.sighted_enemy_units };
      cur[unitName] = (cur[unitName] || 0) + count;
      return { snapshot: { ...state.snapshot, sighted_enemy_units: cur } };
    });
  },
  removeSightedUnit: (unitName, count = 1) => {
    set((state) => {
      const cur = { ...state.snapshot.sighted_enemy_units };
      if (cur[unitName]) {
        cur[unitName] -= count;
        if (cur[unitName] <= 0) delete cur[unitName];
      }
      return { snapshot: { ...state.snapshot, sighted_enemy_units: cur } };
    });
  },
  setSightedUnitCount: (unitName, count) => {
    set((state) => {
      const cur = { ...state.snapshot.sighted_enemy_units };
      if (count <= 0) delete cur[unitName];
      else cur[unitName] = count;
      return { snapshot: { ...state.snapshot, sighted_enemy_units: cur } };
    });
  },
  clearSightedUnits: () => {
    set((state) => ({
      snapshot: { ...state.snapshot, sighted_enemy_units: {} },
    }));
  },

  // Sighted Buildings
  addSightedBuilding: (bldgName, count = 1) => {
    set((state) => {
      const cur = { ...state.snapshot.sighted_enemy_buildings };
      cur[bldgName] = (cur[bldgName] || 0) + count;
      return { snapshot: { ...state.snapshot, sighted_enemy_buildings: cur } };
    });
  },
  removeSightedBuilding: (bldgName, count = 1) => {
    set((state) => {
      const cur = { ...state.snapshot.sighted_enemy_buildings };
      if (cur[bldgName]) {
        cur[bldgName] -= count;
        if (cur[bldgName] <= 0) delete cur[bldgName];
      }
      return { snapshot: { ...state.snapshot, sighted_enemy_buildings: cur } };
    });
  },
  setSightedBuildingCount: (bldgName, count) => {
    set((state) => {
      const cur = { ...state.snapshot.sighted_enemy_buildings };
      if (count <= 0) delete cur[bldgName];
      else cur[bldgName] = count;
      return { snapshot: { ...state.snapshot, sighted_enemy_buildings: cur } };
    });
  },
  clearSightedBuildings: () => {
    set((state) => ({
      snapshot: { ...state.snapshot, sighted_enemy_buildings: {} },
    }));
  },

  // Metadata
  civs: [],
  units: [],
  presets: [],
  selectedPresetId: null,
  loadMetadata: async () => {
    try {
      const [civs, units, presets] = await Promise.all([
        api.getCivs().catch(() => []),
        api.getUnits().catch(() => []),
        api.getPresets().catch(() => []),
      ]);
      set({ civs, units, presets });
    } catch (e) {
      console.error("Failed to load metadata:", e);
    }
  },
  applyPreset: (preset) => {
    set({
      snapshot: { ...preset.snapshot },
      selectedPresetId: preset.id,
      completedChecklistItems: {},
    });
  },

  // Recommendation Inference
  recommendation: null,
  isLoading: false,
  error: null,
  getTacticalRecommendation: async () => {
    set({ isLoading: true, error: null });
    try {
      const snap = get().snapshot;
      const rec = await api.getRecommendation(snap);
      set({
        recommendation: rec,
        isLoading: false,
        completedChecklistItems: {},
      });
    } catch (err: unknown) {
      set({
        error: err instanceof Error ? err.message : "Failed to generate tactical recommendation",
        isLoading: false,
      });
    }
  },

  // Checklist
  completedChecklistItems: {},
  toggleChecklistItem: (item) => {
    set((state) => {
      const next = { ...state.completedChecklistItems };
      next[item] = !next[item];
      return { completedChecklistItems: next };
    });
  },

  // Voice Input
  isListening: false,
  voiceTranscript: "",
  voiceConfidence: 0.0,
  voiceFeedback: null,
  setIsListening: (val) => set({ isListening: val }),
  setVoiceTranscript: (transcript) => set({ voiceTranscript: transcript }),
  applyVoiceTranscript: async (transcript) => {
    set({ isLoading: true, voiceTranscript: transcript });
    try {
      const curSnap = get().snapshot;
      const res = await api.parseVoice(transcript, curSnap);
      set({
        snapshot: res.parsed_snapshot,
        voiceConfidence: res.confidence_score,
        voiceFeedback: res.feedback_message,
        isLoading: false,
      });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      set({
        voiceFeedback: `Voice parse error: ${msg}`,
        isLoading: false,
      });
    }
  },

  // System Health
  health: null,
  checkHealth: async () => {
    try {
      const h = await api.getHealth();
      set({ health: h });
    } catch {
      set({
        health: {
          status: "offline",
          version: "1.0.0",
          onnx_loaded: false,
          llm_connected: false,
          civs_count: 0,
          units_count: 0,
        },
      });
    }
  },
}));
