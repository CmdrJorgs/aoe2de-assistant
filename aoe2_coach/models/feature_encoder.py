"""
Feature Encoder & State Vectorizer for AoE2 Coach Machine Learning Models.

Transforms game snapshots, player states, and fog-of-war observations into
high-dimensional numerical feature arrays (float32) for model training and ONNX inference.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import pandas as pd

from aoe2_coach.schemas.game_constants import (
    CIVILIZATIONS,
    CIV_NAME_TO_ID,
    Age,
    get_civ_name,
)
from aoe2_coach.schemas.match import (
    GameSnapshot,
    PlayerState,
    OpponentObservedState,
    ResourceStockpile,
    VillagerAllocation,
    SightedEntity,
)


# Civilization Strategic Archetype Profiles
CIV_ARCHETYPES = {
    # Cavalry civs
    "franks": {"cavalry": 1.0, "archer": 0.2, "infantry": 0.5, "siege": 0.4, "monk": 0.2},
    "magyars": {"cavalry": 1.0, "archer": 0.8, "infantry": 0.3, "siege": 0.2, "monk": 0.2},
    "huns": {"cavalry": 1.0, "archer": 0.8, "infantry": 0.2, "siege": 0.3, "monk": 0.1},
    "berbers": {"cavalry": 1.0, "archer": 0.4, "infantry": 0.2, "siege": 0.3, "monk": 0.4},
    "cumans": {"cavalry": 1.0, "archer": 0.6, "infantry": 0.3, "siege": 0.6, "monk": 0.1},
    "lithuanians": {"cavalry": 1.0, "archer": 0.4, "infantry": 0.5, "siege": 0.3, "monk": 0.8},
    "bulgarians": {"cavalry": 0.9, "archer": 0.2, "infantry": 0.9, "siege": 0.8, "monk": 0.3},
    "tatars": {"cavalry": 0.9, "archer": 0.9, "infantry": 0.2, "siege": 0.7, "monk": 0.2},
    "poles": {"cavalry": 0.9, "archer": 0.4, "infantry": 0.6, "siege": 0.4, "monk": 0.6},
    "burgundians": {"cavalry": 0.9, "archer": 0.3, "infantry": 0.4, "siege": 0.5, "monk": 0.5},
    "persians": {"cavalry": 0.9, "archer": 0.5, "infantry": 0.3, "siege": 0.5, "monk": 0.3},
    "gurjaras": {"cavalry": 1.0, "archer": 0.2, "infantry": 0.3, "siege": 0.3, "monk": 0.4},
    "georgians": {"cavalry": 0.9, "archer": 0.2, "infantry": 0.4, "siege": 0.6, "monk": 0.5},
    # Archer civs
    "britons": {"cavalry": 0.2, "archer": 1.0, "infantry": 0.4, "siege": 0.4, "monk": 0.3},
    "mayans": {"cavalry": 0.0, "archer": 1.0, "infantry": 0.8, "siege": 0.5, "monk": 0.4},
    "ethiopians": {"cavalry": 0.3, "archer": 1.0, "infantry": 0.4, "siege": 0.8, "monk": 0.3},
    "vietnamese": {"cavalry": 0.4, "archer": 1.0, "infantry": 0.3, "siege": 0.4, "monk": 0.3},
    "italians": {"cavalry": 0.4, "archer": 0.9, "infantry": 0.5, "siege": 0.4, "monk": 0.6},
    "chinese": {"cavalry": 0.7, "archer": 0.9, "infantry": 0.7, "siege": 0.6, "monk": 0.5},
    "koreans": {"cavalry": 0.2, "archer": 0.9, "infantry": 0.3, "siege": 0.9, "monk": 0.5},
    "dravidians": {"cavalry": 0.0, "archer": 0.9, "infantry": 0.8, "siege": 0.8, "monk": 0.3},
    # Infantry civs
    "goths": {"cavalry": 0.4, "archer": 0.2, "infantry": 1.0, "siege": 0.3, "monk": 0.2},
    "japanese": {"cavalry": 0.5, "archer": 0.7, "infantry": 1.0, "siege": 0.4, "monk": 0.6},
    "vikings": {"cavalry": 0.4, "archer": 0.7, "infantry": 1.0, "siege": 0.5, "monk": 0.3},
    "aztecs": {"cavalry": 0.0, "archer": 0.8, "infantry": 1.0, "siege": 0.7, "monk": 1.0},
    "incas": {"cavalry": 0.0, "archer": 0.8, "infantry": 1.0, "siege": 0.5, "monk": 0.6},
    "celts": {"cavalry": 0.4, "archer": 0.3, "infantry": 0.9, "siege": 1.0, "monk": 0.3},
    "malians": {"cavalry": 0.7, "archer": 0.6, "infantry": 0.9, "siege": 0.5, "monk": 0.6},
    "romans": {"cavalry": 0.6, "archer": 0.4, "infantry": 1.0, "siege": 0.7, "monk": 0.3},
    "armenians": {"cavalry": 0.4, "archer": 0.7, "infantry": 0.9, "siege": 0.6, "monk": 0.9},
    # Camel / Counter / Monk civs
    "byzantines": {"cavalry": 0.7, "archer": 0.7, "infantry": 0.7, "siege": 0.5, "monk": 0.8},
    "saracens": {"cavalry": 0.8, "archer": 0.8, "infantry": 0.3, "siege": 0.7, "monk": 0.8},
    "hindustanis": {"cavalry": 0.9, "archer": 0.6, "infantry": 0.5, "siege": 0.5, "monk": 0.4},
    "turks": {"cavalry": 0.8, "archer": 0.9, "infantry": 0.2, "siege": 0.8, "monk": 0.3},
    "bohemians": {"cavalry": 0.2, "archer": 0.7, "infantry": 0.6, "siege": 1.0, "monk": 0.9},
    "bengalis": {"cavalry": 0.6, "archer": 0.6, "infantry": 0.4, "siege": 0.6, "monk": 0.9},
    "slavs": {"cavalry": 0.8, "archer": 0.3, "infantry": 0.8, "siege": 0.9, "monk": 0.7},
    "teutons": {"cavalry": 0.8, "archer": 0.3, "infantry": 0.8, "siege": 0.8, "monk": 0.8},
    "portuguese": {"cavalry": 0.6, "archer": 0.7, "infantry": 0.5, "siege": 0.8, "monk": 0.7},
    "spanish": {"cavalry": 0.8, "archer": 0.3, "infantry": 0.5, "siege": 0.5, "monk": 0.9},
    "burmese": {"cavalry": 0.8, "archer": 0.2, "infantry": 0.9, "siege": 0.5, "monk": 0.9},
    "khmer": {"cavalry": 0.8, "archer": 0.5, "infantry": 0.3, "siege": 0.9, "monk": 0.4},
    "malay": {"cavalry": 0.3, "archer": 0.8, "infantry": 0.8, "siege": 0.5, "monk": 0.6},
    "mongols": {"cavalry": 0.9, "archer": 0.9, "infantry": 0.3, "siege": 0.8, "monk": 0.3},
}

DEFAULT_ARCHETYPE = {"cavalry": 0.5, "archer": 0.5, "infantry": 0.5, "siege": 0.5, "monk": 0.5}


# Unit Categorization Mapping for Feature Extraction
UNIT_CATEGORY_MAP = {
    # Cavalry
    "scout_cavalry": "cavalry", "light_cavalry": "cavalry", "hussar": "cavalry",
    "knight": "cavalry", "cavalier": "cavalry", "paladin": "cavalry",
    "camel_rider": "cavalry", "heavy_camel_rider": "cavalry", "imperial_camel_rider": "cavalry",
    "battle_elephant": "cavalry", "elite_battle_elephant": "cavalry",
    "steppe_lancer": "cavalry", "elite_steppe_lancer": "cavalry",
    "shrivamsha_rider": "cavalry", "cataphract": "cavalry", "magyar_huszar": "cavalry",
    "boyar": "cavalry", "keshik": "cavalry", "leitis": "cavalry", "coustillier": "cavalry",
    "monaspa": "cavalry", "war_elephant": "cavalry", "mameluke": "cavalry",
    # Archers
    "archer": "archer", "crossbowman": "archer", "arbalester": "archer",
    "skirmisher": "archer", "elite_skirmisher": "archer", "imperial_skirmisher": "archer",
    "cavalry_archer": "archer", "heavy_cavalry_archer": "archer", "hand_cannoneer": "archer",
    "longbowman": "archer", "chu_ko_nu": "archer", "mangudai": "archer", "plumed_archer": "archer",
    "rattan_archer": "archer", "kipchak": "archer", "camel_archer": "archer",
    "composite_bowman": "archer", "genoese_crossbowman": "archer",
    # Infantry
    "militiaman": "infantry", "man_at_arms": "infantry", "long_swordsman": "infantry",
    "two_handed_swordsman": "infantry", "champion": "infantry",
    "spearman": "infantry", "pikeman": "infantry", "halberdier": "infantry",
    "eagle_scout": "infantry", "eagle_warrior": "infantry", "elite_eagle_warrior": "infantry",
    "huskarl": "infantry", "samurai": "infantry", "berserk": "infantry", "woad_raider": "infantry",
    "jaguar_warrior": "infantry", "kamayuk": "infantry", "shotel_warrior": "infantry",
    "gbeto": "infantry", "karambit_warrior": "infantry", "serjeant": "infantry",
    "obuch": "infantry", "urumi_swordsman": "infantry", "ghulam": "infantry", "legionary": "infantry",
    # Siege
    "battering_ram": "siege", "capped_ram": "siege", "siege_ram": "siege",
    "mangonel": "siege", "onager": "siege", "siege_onager": "siege",
    "scorpion": "siege", "heavy_scorpion": "siege",
    "bombard_cannon": "siege", "trebuchet": "siege", "organ_gun": "siege",
    "ballista_elephant": "siege", "hussite_wagon": "siege", "dromon": "siege",
    # Monk
    "monk": "monk", "missionary": "monk",
}


FEATURE_NAMES: List[str] = [
    # 1. Match & Temporal
    "timestamp_min",
    "player_age",
    "opponent_estimated_age",
    "age_diff",
    "player_elo_norm",
    "opponent_elo_norm",
    "elo_diff_norm",
    # 2. Economy Stockpile
    "food_stockpile_k",
    "wood_stockpile_k",
    "gold_stockpile_k",
    "stone_stockpile_k",
    "total_resources_k",
    "food_to_wood_ratio",
    "gold_to_wood_ratio",
    "is_floating_wood",
    "is_floating_food",
    "is_floating_gold",
    # 3. Economy Villagers
    "vills_total",
    "vills_food",
    "vills_wood",
    "vills_gold",
    "vills_stone",
    "pct_vills_food",
    "pct_vills_wood",
    "pct_vills_gold",
    "pct_vills_stone",
    # 4. Player Military & Tech
    "player_military_total",
    "player_cavalry_count",
    "player_archer_count",
    "player_infantry_count",
    "player_siege_count",
    "player_monk_count",
    "player_tech_count",
    "military_to_vill_ratio",
    # 5. Opponent Sighted Military
    "opp_sighted_military_total",
    "opp_sighted_cavalry",
    "opp_sighted_archers",
    "opp_sighted_infantry",
    "opp_sighted_siege",
    "opp_sighted_monks",
    # 6. Opponent Sighted Buildings
    "opp_sighted_buildings_total",
    "opp_sighted_barracks",
    "opp_sighted_archery_range",
    "opp_sighted_stable",
    "opp_sighted_siege_workshop",
    "opp_sighted_castle",
    "opp_sighted_monastery",
    "opp_sighted_town_center",
    # 7. Civilization Archetype & Affinity Features
    "player_civ_id_norm",
    "opp_civ_id_norm",
    "player_cav_affinity",
    "player_arch_affinity",
    "player_inf_affinity",
    "player_siege_affinity",
    "player_monk_affinity",
    "opp_cav_affinity",
    "opp_arch_affinity",
    "opp_inf_affinity",
    "opp_siege_affinity",
    "opp_monk_affinity",
    # 8. Relative Advantage Estimates
    "rel_military_advantage",
    "rel_villager_advantage_est",
    "rel_cav_vs_opp_archer",
    "rel_archer_vs_opp_inf",
    "rel_inf_vs_opp_cav",
]


class FeatureEncoder:
    """
    Standardized State Vectorizer for AoE2 Coach ML Models.
    Ensures exact feature parity across training and real-time ONNX inference.
    """

    def __init__(self):
        self.feature_names = list(FEATURE_NAMES)
        self.num_features = len(self.feature_names)

    def _get_civ_id_and_name(self, civ: Union[str, int, None]) -> Tuple[int, str]:
        """Normalize civ representation to (id, lowercase_name)."""
        if isinstance(civ, int):
            cid = civ
            cname = CIVILIZATIONS.get(cid, "unknown").lower()
            return cid, cname
        elif isinstance(civ, str):
            cname = civ.lower().strip()
            cid = CIV_NAME_TO_ID.get(cname, 0)
            return cid, cname
        return 0, "unknown"

    def _get_civ_affinities(self, civ_name: str) -> Dict[str, float]:
        """Look up civilization strategic archetype affinities."""
        return CIV_ARCHETYPES.get(civ_name.lower(), DEFAULT_ARCHETYPE)

    def encode_snapshot(self, snapshot: GameSnapshot) -> np.ndarray:
        """Encode a single GameSnapshot instance into a 1D float32 numpy array."""
        player = snapshot.player
        opp = snapshot.opponent_observed

        # Extract counts from military dictionary
        mil_units = player.military_units or {}
        cavalry_cnt = sum(cnt for u, cnt in mil_units.items() if UNIT_CATEGORY_MAP.get(u.lower()) == "cavalry")
        archer_cnt = sum(cnt for u, cnt in mil_units.items() if UNIT_CATEGORY_MAP.get(u.lower()) == "archer")
        infantry_cnt = sum(cnt for u, cnt in mil_units.items() if UNIT_CATEGORY_MAP.get(u.lower()) == "infantry")
        siege_cnt = sum(cnt for u, cnt in mil_units.items() if UNIT_CATEGORY_MAP.get(u.lower()) == "siege")
        monk_cnt = sum(cnt for u, cnt in mil_units.items() if UNIT_CATEGORY_MAP.get(u.lower()) == "monk")
        total_mil = sum(mil_units.values())

        # Extract sighted opponent unit categories
        opp_cavalry = 0
        opp_archers = 0
        opp_infantry = 0
        opp_siege = 0
        opp_monks = 0
        for u in opp.sighted_units:
            cat = UNIT_CATEGORY_MAP.get(u.entity_name.lower(), "other")
            if cat == "cavalry":
                opp_cavalry += u.count
            elif cat == "archer":
                opp_archers += u.count
            elif cat == "infantry":
                opp_infantry += u.count
            elif cat == "siege":
                opp_siege += u.count
            elif cat == "monk":
                opp_monks += u.count
        opp_total_mil = opp_cavalry + opp_archers + opp_infantry + opp_siege + opp_monks

        # Extract sighted opponent buildings
        opp_bld_counts = {"barracks": 0, "archery_range": 0, "stable": 0, "siege_workshop": 0, "castle": 0, "monastery": 0, "town_center": 0}
        for b in opp.sighted_buildings:
            bname = b.entity_name.lower()
            if bname in opp_bld_counts:
                opp_bld_counts[bname] += b.count
        opp_total_bld = sum(b.count for b in opp.sighted_buildings)

        # Prepare state dict and encode
        state_dict = {
            "timestamp_sec": snapshot.timestamp_sec,
            "player_civ": player.civ_name or player.civ_id,
            "player_age": player.age,
            "player_elo": player.elo or 1200,
            "food": player.resources.food,
            "wood": player.resources.wood,
            "gold": player.resources.gold,
            "stone": player.resources.stone,
            "vills_total": player.villagers.total,
            "vills_food": player.villagers.food,
            "vills_wood": player.villagers.wood,
            "vills_gold": player.villagers.gold,
            "vills_stone": player.villagers.stone,
            "military_total": total_mil,
            "cavalry_count": cavalry_cnt,
            "archer_count": archer_cnt,
            "infantry_count": infantry_cnt,
            "siege_count": siege_cnt,
            "monk_count": monk_cnt,
            "tech_count": len(player.completed_techs),
            "opponent_civ": opp.civ_name or opp.civ_id,
            "opponent_estimated_age": opp.estimated_age,
            "opponent_elo": 1200,
            "opp_sighted_military_total": opp_total_mil,
            "opp_sighted_cavalry": opp_cavalry,
            "opp_sighted_archers": opp_archers,
            "opp_sighted_infantry": opp_infantry,
            "opp_sighted_siege": opp_siege,
            "opp_sighted_monks": opp_monks,
            "opp_sighted_buildings_total": opp_total_bld,
            "opp_sighted_barracks": opp_bld_counts["barracks"],
            "opp_sighted_archery_range": opp_bld_counts["archery_range"],
            "opp_sighted_stable": opp_bld_counts["stable"],
            "opp_sighted_siege_workshop": opp_bld_counts["siege_workshop"],
            "opp_sighted_castle": opp_bld_counts["castle"],
            "opp_sighted_monastery": opp_bld_counts["monastery"],
            "opp_sighted_town_center": opp_bld_counts["town_center"],
        }
        return self.encode_dict(state_dict)

    def encode_dict(self, state: Dict[str, Any]) -> np.ndarray:
        """Encode raw feature dictionary into a 1D float32 array."""
        t_sec = float(state.get("timestamp_sec", 600))
        t_min = t_sec / 60.0

        p_age = float(state.get("player_age", 2))
        opp_age = float(state.get("opponent_estimated_age", p_age))
        age_diff = p_age - opp_age

        p_elo = float(state.get("player_elo", 1200))
        opp_elo = float(state.get("opponent_elo", p_elo))
        p_elo_norm = (p_elo - 1000.0) / 500.0
        opp_elo_norm = (opp_elo - 1000.0) / 500.0
        elo_diff_norm = (p_elo - opp_elo) / 200.0

        # Resources
        food = float(state.get("food", state.get("player_food", 200)))
        wood = float(state.get("wood", state.get("player_wood", 200)))
        gold = float(state.get("gold", state.get("player_gold", 100)))
        stone = float(state.get("stone", state.get("player_stone", 0)))
        total_res = food + wood + gold + stone

        food_k = food / 1000.0
        wood_k = wood / 1000.0
        gold_k = gold / 1000.0
        stone_k = stone / 1000.0
        total_res_k = total_res / 1000.0

        food_wood_ratio = food / max(1.0, wood)
        gold_wood_ratio = gold / max(1.0, wood)

        is_floating_wood = 1.0 if (wood >= 600 and (food < 200 or gold < 100)) else 0.0
        is_floating_food = 1.0 if (food >= 1000 and wood < 150) else 0.0
        is_floating_gold = 1.0 if (gold >= 800 and food < 150) else 0.0

        # Villagers
        vills_tot = float(state.get("vills_total", state.get("player_vills_total", 30)))
        vills_f = float(state.get("vills_food", state.get("player_vills_food", 12)))
        vills_w = float(state.get("vills_wood", state.get("player_vills_wood", 12)))
        vills_g = float(state.get("vills_gold", state.get("player_vills_gold", 4)))
        vills_s = float(state.get("vills_stone", state.get("player_vills_stone", 0)))

        denom_v = max(1.0, vills_tot)
        pct_f = vills_f / denom_v
        pct_w = vills_w / denom_v
        pct_g = vills_g / denom_v
        pct_s = vills_s / denom_v

        # Military
        mil_tot = float(state.get("military_total", state.get("player_military_total", 0)))
        mil_cav = float(state.get("cavalry_count", 0))
        mil_arch = float(state.get("archer_count", 0))
        mil_inf = float(state.get("infantry_count", 0))
        mil_siege = float(state.get("siege_count", 0))
        mil_monk = float(state.get("monk_count", 0))
        tech_cnt = float(state.get("tech_count", state.get("player_tech_count", 2)))

        mil_to_vill = mil_tot / max(1.0, vills_tot)

        # Opponent military
        opp_mil_tot = float(state.get("opp_sighted_military_total", state.get("opponent_sighted_units_count", 0)))
        opp_mil_cav = float(state.get("opp_sighted_cavalry", 0))
        opp_mil_arch = float(state.get("opp_sighted_archers", 0))
        opp_mil_inf = float(state.get("opp_sighted_infantry", 0))
        opp_mil_siege = float(state.get("opp_sighted_siege", 0))
        opp_mil_monk = float(state.get("opp_sighted_monks", 0))

        # Opponent buildings
        opp_bld_tot = float(state.get("opp_sighted_buildings_total", state.get("opponent_sighted_buildings_count", 0)))
        opp_barracks = float(state.get("opp_sighted_barracks", 0))
        opp_archery = float(state.get("opp_sighted_archery_range", 0))
        opp_stable = float(state.get("opp_sighted_stable", 0))
        opp_siege_w = float(state.get("opp_sighted_siege_workshop", 0))
        opp_castle = float(state.get("opp_sighted_castle", 0))
        opp_monastery = float(state.get("opp_sighted_monastery", 0))
        opp_tc = float(state.get("opp_sighted_town_center", 0))

        # Civ archetypes
        p_cid, p_cname = self._get_civ_id_and_name(state.get("player_civ", state.get("player_civ_name", state.get("player_civ_id"))))
        opp_cid, opp_cname = self._get_civ_id_and_name(state.get("opponent_civ", state.get("opponent_civ_name", state.get("opponent_civ_id"))))

        p_aff = self._get_civ_affinities(p_cname)
        opp_aff = self._get_civ_affinities(opp_cname)

        p_cid_norm = p_cid / 50.0
        opp_cid_norm = opp_cid / 50.0

        # Relative advantages
        rel_mil_adv = (mil_tot - opp_mil_tot) / max(1.0, mil_tot + opp_mil_tot)
        rel_vill_adv = (vills_tot - (opp_age * 12.0 + t_min * 1.5)) / max(1.0, vills_tot)
        rel_cav_vs_arch = (mil_cav - opp_mil_arch) / max(1.0, mil_cav + opp_mil_arch)
        rel_arch_vs_inf = (mil_arch - opp_mil_inf) / max(1.0, mil_arch + opp_mil_inf)
        rel_inf_vs_cav = (mil_inf - opp_mil_cav) / max(1.0, mil_inf + opp_mil_cav)

        features = [
            t_min,
            p_age,
            opp_age,
            age_diff,
            p_elo_norm,
            opp_elo_norm,
            elo_diff_norm,
            food_k,
            wood_k,
            gold_k,
            stone_k,
            total_res_k,
            food_wood_ratio,
            gold_wood_ratio,
            is_floating_wood,
            is_floating_food,
            is_floating_gold,
            vills_tot,
            vills_f,
            vills_w,
            vills_g,
            vills_s,
            pct_f,
            pct_w,
            pct_g,
            pct_s,
            mil_tot,
            mil_cav,
            mil_arch,
            mil_inf,
            mil_siege,
            mil_monk,
            tech_cnt,
            mil_to_vill,
            opp_mil_tot,
            opp_mil_cav,
            opp_mil_arch,
            opp_mil_inf,
            opp_mil_siege,
            opp_mil_monk,
            opp_bld_tot,
            opp_barracks,
            opp_archery,
            opp_stable,
            opp_siege_w,
            opp_castle,
            opp_monastery,
            opp_tc,
            p_cid_norm,
            opp_cid_norm,
            p_aff["cavalry"],
            p_aff["archer"],
            p_aff["infantry"],
            p_aff["siege"],
            p_aff["monk"],
            opp_aff["cavalry"],
            opp_aff["archer"],
            opp_aff["infantry"],
            opp_aff["siege"],
            opp_aff["monk"],
            rel_mil_adv,
            rel_vill_adv,
            rel_cav_vs_arch,
            rel_arch_vs_inf,
            rel_inf_vs_cav,
        ]

        return np.array(features, dtype=np.float32)

    def encode_batch(self, snapshots: List[Union[GameSnapshot, Dict[str, Any]]]) -> np.ndarray:
        """Encode a batch of snapshots or dictionaries into a 2D float32 array (N, D)."""
        if not snapshots:
            return np.empty((0, self.num_features), dtype=np.float32)

        encoded_rows = []
        for s in snapshots:
            if isinstance(s, GameSnapshot):
                encoded_rows.append(self.encode_snapshot(s))
            elif isinstance(s, dict):
                encoded_rows.append(self.encode_dict(s))
            else:
                raise TypeError(f"Unsupported snapshot type: {type(s)}")

        return np.vstack(encoded_rows)

    def encode_dataframe(self, df: pd.DataFrame) -> np.ndarray:
        """Encode a pandas DataFrame containing flat parquet snapshot records."""
        records = df.to_dict(orient="records")
        return self.encode_batch(records)
