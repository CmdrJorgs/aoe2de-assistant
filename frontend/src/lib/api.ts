/**
 * API Client for AoE2 Coach Backend Gateway
 */

import {
  SnapshotInput,
  RecommendationResponse,
  PresetScenario,
  CivMetadata,
  UnitMetadata,
  VoiceParseResponse,
  CombatSimRequest,
  CombatSimResponse,
  HealthResponse,
} from "@/types/coach";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return res.json() as Promise<T>;
}

export const api = {
  // System Health
  getHealth: (): Promise<HealthResponse> => {
    return fetchJson<HealthResponse>("/api/health");
  },

  // Full Tactical Recommendation
  getRecommendation: (snapshot: SnapshotInput): Promise<RecommendationResponse> => {
    return fetchJson<RecommendationResponse>("/api/tactical/recommend", {
      method: "POST",
      body: JSON.stringify(snapshot),
    });
  },

  // Voice Transcript Parser
  parseVoice: (transcript: string, currentSnapshot?: SnapshotInput): Promise<VoiceParseResponse> => {
    return fetchJson<VoiceParseResponse>("/api/tactical/voice-parse", {
      method: "POST",
      body: JSON.stringify({
        transcript,
        current_snapshot: currentSnapshot,
      }),
    });
  },

  // Combat Simulator
  simulateCombat: (req: CombatSimRequest): Promise<CombatSimResponse> => {
    return fetchJson<CombatSimResponse>("/api/tactical/simulate", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  // Metadata
  getCivs: (): Promise<CivMetadata[]> => {
    return fetchJson<CivMetadata[]>("/api/meta/civs");
  },

  getUnits: (): Promise<UnitMetadata[]> => {
    return fetchJson<UnitMetadata[]>("/api/meta/units");
  },

  getPresets: (): Promise<PresetScenario[]> => {
    return fetchJson<PresetScenario[]>("/api/meta/presets");
  },
};
