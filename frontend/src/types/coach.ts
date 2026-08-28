/**
 * AoE2 Coach TypeScript Interfaces and Types
 */

export type AgeNumber = 1 | 2 | 3 | 4;

export interface ResourceStockpile {
  food: number;
  wood: number;
  gold: number;
  stone: number;
}

export interface VillagerAllocation {
  total?: number;
  food: number;
  wood: number;
  gold: number;
  stone: number;
  idle_rate?: number;
}

export interface SnapshotInput {
  player_civ: string;
  opponent_civ: string;
  player_elo: number;
  game_time_minutes: number;
  current_age: AgeNumber;
  food: number;
  wood: number;
  gold: number;
  stone: number;
  vills_food: number;
  vills_wood: number;
  vills_gold: number;
  vills_stone: number;
  vills_total?: number;
  military_units: Record<string, number>;
  player_buildings: Record<string, number>;
  completed_techs: string[];
  sighted_enemy_units: Record<string, number>;
  sighted_enemy_buildings: Record<string, number>;
  opponent_estimated_age?: number;
  user_notes?: string;
  force_fallback: boolean;
  elo_tier_override?: string;
}

export interface MatchContext {
  player_civ: string;
  opponent_civ: string;
  player_elo: number;
  player_age: number;
  player_age_name: string;
  game_time_sec: number;
  formatted_time: string;
}

export interface WinProbability {
  win_probability: number;
  win_probability_percent?: string;
  advantage_level: string;
  eco_advantage_score?: number;
  military_advantage_score?: number;
  civ_matchup_score?: number;
  key_win_factors?: string[];
  summary?: string;
}

export interface CompositionRanking {
  composition: string;
  confidence: number;
  recommended_building: string;
  key_technologies: string[];
  strategic_rationale: string;
}

export interface MilitaryActionPlan {
  primary_composition: string;
  confidence: number;
  secondary_composition?: string | null;
  recommended_building?: string;
  recommended_tech_focus?: string;
  rankings?: CompositionRanking[];
  strategic_summary?: string;
  tactical_notes?: string;
  recommended_tech_order?: string[];
}

export interface ThreatAnalysis {
  primary_threat_archetype: string;
  detected_armor_classes: string[];
  dominant_enemy_unit: string;
  total_enemy_count: number;
  threat_level: "low" | "medium" | "high" | "critical" | string;
  tactical_warning: string;
}

export interface CounterOption {
  unit_id: string;
  unit_name: string;
  counter_type: string;
  effectiveness_score: number;
  production_building: string;
  key_technologies: string[];
  tactical_rationale: string;
  civ_synergy_note?: string;
}

export interface CounterMatrixData {
  threat_analysis: ThreatAnalysis;
  recommended_counters: CounterOption[];
  primary_unit_recommendation: string;
  secondary_support_unit?: string | null;
  production_building_target: string;
  tactical_summary: string;
}

export interface MacroRebalancePlan {
  current_allocation: VillagerAllocation;
  target_allocation: VillagerAllocation;
  villager_shifts: Record<string, number>;
  shift_instructions?: string[];
  floating_stockpile_warnings?: string[];
  farm_reseeding_wood_tax_per_sec?: number;
  macro_health_grade?: string;
  summary?: string;
  identified_economic_bottlenecks?: string[];
  actionable_rebalance_order?: string;
  production_sustainability_status?: string;
}

export interface StanceTimingData {
  recommended_stance?: string;
  stance_class?: string;
  stance_confidence?: number;
  confidence?: number;
  attack_window_sec?: number;
  urgency?: string;
  civ_power_spike?: string;
  threat_spike_alert?: string;
  power_spike_source?: string;
  threat_alert?: string;
  tactical_directive?: string;
  summary?: string;
  is_attack_window_active?: boolean;
}

export interface TacticalMilitaryAdvice {
  primary_unit_recommendation: string;
  secondary_unit_recommendation?: string | null;
  production_building_instruction: string;
  key_tech_priorities: string[];
  counter_explanation: string;
  micro_positioning_tip?: string | null;
}

export interface TacticalEconomyAdvice {
  problem_diagnosis: string;
  immediate_action: string;
  target_villager_allocation: Record<string, number>;
  macro_tip: string;
}

export interface TacticalTimingAdvice {
  posture: string;
  attack_window: string;
  threat_alert?: string | null;
  strategic_spike_reasoning: string;
}

export interface CoachingExplanationData {
  primary_directive: string;
  coach_summary: string;
  elo_tier: string;
  military_plan: TacticalMilitaryAdvice;
  economic_plan: TacticalEconomyAdvice;
  timing_plan: TacticalTimingAdvice;
  priority_checklist: string[];
}

export interface VerifiedCoachingExplanation {
  explanation: CoachingExplanationData;
  is_valid: boolean;
  corrections_applied: string[];
  was_fallback: boolean;
  generation_latency_ms: number;
}

export interface RecommendationResponse {
  match_context: MatchContext;
  primary_directive: string;
  win_probability: WinProbability;
  military_action_plan: MilitaryActionPlan;
  counter_matrix: CounterMatrixData;
  economic_rebalance: MacroRebalancePlan;
  tactical_stance: StanceTimingData;
  actionable_checklist: string[];
  explanation: VerifiedCoachingExplanation;
  inference_latency_ms: number;
  explanation_latency_ms: number;
  total_latency_ms: number;
}

export interface PresetScenario {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  snapshot: SnapshotInput;
}

export interface CivMetadata {
  id: number;
  name: string;
  architecture: string;
  bonuses: string[];
  unique_units: string[];
  castle_unique_tech?: string | null;
  imperial_unique_tech?: string | null;
  team_bonus: string;
}

export interface UnitMetadata {
  id: string;
  name: string;
  category: string;
  age: number;
  hp: number;
  attack: number;
  melee_armor: number;
  pierce_armor: number;
  range: number;
  reload_time: number;
  train_time: number;
  cost: {
    food: number;
    wood: number;
    gold: number;
    stone: number;
    total: number;
  };
}

export interface VoiceParseResponse {
  parsed_snapshot: SnapshotInput;
  extracted_entities: Record<string, unknown>;
  confidence_score: number;
  feedback_message: string;
}

export interface CombatSimRequest {
  attacker_unit: string;
  attacker_count: number;
  attacker_civ: string;
  attacker_upgrades?: string[];
  defender_unit: string;
  defender_count: number;
  defender_civ: string;
  defender_upgrades?: string[];
  elevation_diff?: number;
}

export interface CombatSimResponse {
  attacker_unit: string;
  attacker_count: number;
  defender_unit: string;
  defender_count: number;
  single_hit_attacker_to_defender: number;
  single_hit_defender_to_attacker: number;
  simulated_winner: string;
  time_to_kill_seconds: number;
  remaining_attackers: number;
  remaining_defenders: number;
  cost_efficiency_ratio: number;
  tactical_summary: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  onnx_loaded: boolean;
  llm_connected: boolean;
  civs_count: number;
  units_count: number;
}
