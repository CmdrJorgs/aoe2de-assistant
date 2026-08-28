"""
AoE2 Speech & Natural Language Transcript Parser:
Translates spoken or freeform text into structured AoE2 snapshot states.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from aoe2_coach.schemas.game_constants import CIVILIZATIONS, CIV_NAME_TO_ID, Age
from aoe2_coach.api.schemas import SnapshotInput, VoiceParseResponse

logger = logging.getLogger(__name__)

# Number word mapping
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100, "a": 1, "an": 1,
}

# Unit aliases for common speech patterns
UNIT_ALIASES: Dict[str, str] = {
    "archer": "Archer", "archers": "Archer", "xbow": "Crossbowman", "crossbow": "Crossbowman",
    "crossbows": "Crossbowman", "crossbowman": "Crossbowman", "crossbowmen": "Crossbowman",
    "arbalest": "Arbalester", "arbalester": "Arbalester", "arbalests": "Arbalester", "arbs": "Arbalester",
    "skirm": "Skirmisher", "skirms": "Skirmisher", "skirmisher": "Skirmisher", "skirmishers": "Skirmisher",
    "elite skirm": "Elite Skirmisher", "elite skirmisher": "Elite Skirmisher", "elite skirms": "Elite Skirmisher",
    "hand cannoneer": "Hand Cannoneer", "hand cannoneers": "Hand Cannoneer", "hc": "Hand Cannoneer", "gunpowder": "Hand Cannoneer",
    "cav archer": "Cavalry Archer", "cav archers": "Cavalry Archer", "cavalry archer": "Cavalry Archer", "ca": "Cavalry Archer",
    "militia": "Militia", "man at arms": "Man-at-Arms", "maa": "Man-at-Arms", "men at arms": "Man-at-Arms",
    "longsword": "Long Swordsman", "longswordsman": "Long Swordsman", "two handed swordsman": "Two-Handed Swordsman",
    "champion": "Champion", "champions": "Champion", "champs": "Champion",
    "spearman": "Spearman", "spearmen": "Spearman", "spears": "Spearman",
    "pike": "Pikeman", "pikes": "Pikeman", "pikeman": "Pikeman", "pikemen": "Pikeman",
    "halberdier": "Halberdier", "halberdiers": "Halberdier", "halb": "Halberdier", "halbs": "Halberdier",
    "eagle": "Eagle Scout", "eagles": "Eagle Scout", "eagle warrior": "Eagle Warrior", "eagle warriors": "Eagle Warrior",
    "scout": "Scout Cavalry", "scouts": "Scout Cavalry", "scout cav": "Scout Cavalry", "scout cavalry": "Scout Cavalry",
    "light cav": "Light Cavalry", "light cavalry": "Light Cavalry", "lcav": "Light Cavalry",
    "hussar": "Hussar", "hussars": "Hussar",
    "knight": "Knight", "knights": "Knight", "kt": "Knight", "kts": "Knight",
    "cavalier": "Cavalier", "cavaliers": "Cavalier", "paladin": "Paladin", "paladins": "Paladin",
    "camel": "Camel Rider", "camels": "Camel Rider", "camel rider": "Camel Rider",
    "heavy camel": "Heavy Camel Rider", "elephant": "Battle Elephant", "elephants": "Battle Elephant",
    "ram": "Battering Ram", "rams": "Battering Ram", "battering ram": "Battering Ram",
    "capped ram": "Capped Ram", "siege ram": "Siege Ram",
    "mangonel": "Mangonel", "mangonels": "Mangonel", "mango": "Mangonel", "mangos": "Mangonel",
    "onager": "Onager", "onagers": "Onager", "siege onager": "Siege Onager",
    "scorpion": "Scorpion", "scorpions": "Scorpion", "treb": "Trebuchet", "trebuchet": "Trebuchet",
    "trebuchets": "Trebuchet", "trebs": "Trebuchet", "bombard cannon": "Bombard Cannon", "bbc": "Bombard Cannon",
    "monk": "Monk", "monks": "Monk",
    # Unique Units
    "longbow": "Longbowman", "longbowman": "Longbowman", "longbowmen": "Longbowman",
    "cataphract": "Cataphract", "cataphracts": "Cataphract",
    "woad": "Woad Raider", "woad raider": "Woad Raider", "woads": "Woad Raider",
    "chu ko nu": "Chu Ko Nu", "chukonu": "Chu Ko Nu",
    "thrower": "Throwing Axeman", "throwing axeman": "Throwing Axeman", "axeman": "Throwing Axeman",
    "huskarl": "Huskarl", "huskarls": "Huskarl",
    "samurai": "Samurai", "mangudai": "Mangudai",
    "war elephant": "War Elephant", "mameluke": "Mameluke", "mamelukes": "Mameluke",
    "teutonic knight": "Teutonic Knight", "tk": "Teutonic Knight",
    "janissary": "Janissary", "janissaries": "Janissary", "jans": "Janissary",
    "berserk": "Berserk", "berserker": "Berserk", "berserkers": "Berserk", "berserks": "Berserk",
    "jaguar": "Jaguar Warrior", "jaguar warrior": "Jaguar Warrior", "jags": "Jaguar Warrior",
    "plumed archer": "Plumed Archer", "plumes": "Plumed Archer",
    "conquistador": "Conquistador", "conq": "Conquistador", "conqs": "Conquistador", "conquistadors": "Conquistador",
    "tarkan": "Tarkan", "tarkans": "Tarkan",
    "war wagon": "War Wagon", "war wagons": "War Wagon",
    "plumed": "Plumed Archer", "boyar": "Boyar", "boyars": "Boyar",
    "kamayuk": "Kamayuk", "kamayuks": "Kamayuk", "camel archer": "Camel Archer",
    "genitour": "Genitour", "shotel": "Shotel Warrior", "shotels": "Shotel Warrior",
    "gbeto": "Gbeto", "gbetos": "Gbeto", "organ gun": "Organ Gun", "organ guns": "Organ Gun",
    "caravel": "Caravel", "rattan": "Rattan Archer", "rattan archer": "Rattan Archer",
    "ballista elephant": "Ballista Elephant", "konnik": "Konnik", "konniks": "Konnik",
    "keshik": "Keshik", "keshiks": "Keshik", "kipchak": "Kipchak", "kipchaks": "Kipchak",
    "leitis": "Leitis", "coustillier": "Coustillier", "serjeant": "Serjeant",
    "obuch": "Obuch", "hussite wagon": "Hussite Wagon", "shrivamsha": "Shrivamsha Rider",
    "shrivamsha rider": "Shrivamsha Rider", "ghulam": "Ghulam", "ghulams": "Ghulam",
    "urumi": "Urumi Swordsman", "chakram": "Chakram Thrower", "composite bowman": "Composite Bowman",
    "centurion": "Centurion", "legionary": "Legionary", "monaspa": "Monaspa",
}

# Building aliases
BUILDING_ALIASES: Dict[str, str] = {
    "town center": "Town Center", "town centre": "Town Center", "tc": "Town Center", "tcs": "Town Center",
    "barracks": "Barracks", "rax": "Barracks",
    "range": "Archery Range", "ranges": "Archery Range", "archery range": "Archery Range", "archery ranges": "Archery Range",
    "stable": "Stable", "stables": "Stable",
    "siege workshop": "Siege Workshop", "workshop": "Siege Workshop", "workshops": "Siege Workshop", "siege": "Siege Workshop",
    "monastery": "Monastery", "monasteries": "Monastery",
    "blacksmith": "Blacksmith", "market": "Market", "university": "University",
    "castle": "Castle", "castles": "Castle",
    "dock": "Dock", "docks": "Dock", "tower": "Watch Tower", "towers": "Watch Tower",
    "outpost": "Outpost", "wall": "Stone Wall", "walls": "Stone Wall", "gate": "Gate",
}


def parse_number_expression(text: str) -> Optional[int]:
    """Parse integer from digits or word combinations (e.g. 'twenty five' -> 25)."""
    text = text.strip().lower()
    if text.isdigit():
        return int(text)
    
    words = text.split()
    total = 0
    current = 0
    for w in words:
        if w in NUMBER_WORDS:
            val = NUMBER_WORDS[w]
            if val == 100:
                current = (current if current != 0 else 1) * 100
            elif val >= 20:
                current += val
            else:
                current += val
        elif w.isdigit():
            current += int(w)
    total += current
    return total if total > 0 or "zero" in words or text == "0" else None


class VoiceTranscriptParser:
    """
    Parser for conversational voice transcripts into AoE2 match snapshot structures.
    """

    @classmethod
    def parse(
        cls,
        transcript: str,
        current_snapshot: Optional[SnapshotInput] = None,
    ) -> VoiceParseResponse:
        snapshot = current_snapshot.model_copy() if current_snapshot else SnapshotInput()
        extracted: Dict[str, Any] = {}
        feedback_notes: List[str] = []
        raw_lower = transcript.lower()

        # 1. Match Civs (Player and Opponent)
        # e.g., "I'm playing Franks vs Vikings", "playing as Britons against Mayans", "my civ is Mongols"
        civ_names = list(CIVILIZATIONS.values())
        found_civs: List[str] = []
        for civ in civ_names:
            pattern = rf"\b{re.escape(civ.lower())}\b"
            if re.search(pattern, raw_lower):
                found_civs.append(civ)

        # Check matchup patterns
        vs_match = re.search(r"(\w+)\s+(?:vs|versus|against)\s+(\w+)", raw_lower)
        if vs_match:
            c1_str, c2_str = vs_match.group(1), vs_match.group(2)
            c1_match = next((c for c in civ_names if c.lower() == c1_str), None)
            c2_match = next((c for c in civ_names if c.lower() == c2_str), None)
            if c1_match:
                snapshot.player_civ = c1_match
                extracted["player_civ"] = c1_match
                feedback_notes.append(f"Player civ set to {c1_match}")
            if c2_match:
                snapshot.opponent_civ = c2_match
                extracted["opponent_civ"] = c2_match
                feedback_notes.append(f"Opponent civ set to {c2_match}")
        elif found_civs:
            if "i'm playing" in raw_lower or "i am playing" in raw_lower or "playing as" in raw_lower or "my civ" in raw_lower:
                snapshot.player_civ = found_civs[0]
                extracted["player_civ"] = found_civs[0]
                feedback_notes.append(f"Player civ set to {found_civs[0]}")
                if len(found_civs) > 1:
                    snapshot.opponent_civ = found_civs[1]
                    extracted["opponent_civ"] = found_civs[1]
                    feedback_notes.append(f"Opponent civ set to {found_civs[1]}")
            elif "opponent" in raw_lower or "enemy" in raw_lower or "facing" in raw_lower:
                snapshot.opponent_civ = found_civs[0]
                extracted["opponent_civ"] = found_civs[0]
                feedback_notes.append(f"Opponent civ set to {found_civs[0]}")

        # 2. Match ELO
        elo_match = re.search(r"(?:elo|rating|rank)\s*(?:is|of|at|around)?\s*(\d{3,4})", raw_lower)
        if not elo_match:
            elo_match = re.search(r"(\d{3,4})\s*(?:elo|rating)", raw_lower)
        if elo_match:
            elo_val = int(elo_match.group(1))
            if 400 <= elo_val <= 3000:
                snapshot.player_elo = elo_val
                extracted["player_elo"] = elo_val
                feedback_notes.append(f"ELO set to {elo_val}")

        # 3. Match Game Time
        time_match = re.search(r"(?:minute|min|time|at)\s*(\d{1,2})(?::(\d{2}))?", raw_lower)
        if not time_match:
            time_match = re.search(r"(\d{1,2})(?::(\d{2}))\s*(?:min|minutes)?", raw_lower)
        if time_match:
            mins = float(time_match.group(1))
            secs = float(time_match.group(2)) if time_match.group(2) else 0.0
            total_mins = mins + (secs / 60.0)
            if 0.0 <= total_mins <= 120.0:
                snapshot.game_time_minutes = round(total_mins, 1)
                extracted["game_time_minutes"] = snapshot.game_time_minutes
                feedback_notes.append(f"Game time set to {snapshot.game_time_minutes}m")

        # 4. Match Current Age
        if "imperial" in raw_lower or " imp " in f" {raw_lower} " or "post imp" in raw_lower:
            snapshot.current_age = 4
            extracted["current_age"] = "Imperial Age"
            feedback_notes.append("Age set to Imperial")
        elif "castle" in raw_lower or "castle age" in raw_lower:
            snapshot.current_age = 3
            extracted["current_age"] = "Castle Age"
            feedback_notes.append("Age set to Castle")
        elif "feudal" in raw_lower or "feudal age" in raw_lower:
            snapshot.current_age = 2
            extracted["current_age"] = "Feudal Age"
            feedback_notes.append("Age set to Feudal")
        elif "dark age" in raw_lower or "dark" in raw_lower:
            snapshot.current_age = 1
            extracted["current_age"] = "Dark Age"
            feedback_notes.append("Age set to Dark")

        # 5. Match Resource Stockpiles
        # e.g., "750 wood", "320 food", "120 gold", "450 stone", "wood is 750", "floating 800 wood"
        for res, attr in [("food", "food"), ("wood", "wood"), ("gold", "gold"), ("stone", "stone")]:
            m = re.search(rf"(\d+)\s*(?:of\s+)?{res}\b", raw_lower)
            if not m:
                m = re.search(rf"{res}\s*(?:is|stockpile|count|has)?\s*(\d+)", raw_lower)
            if m:
                val = int(m.group(1))
                setattr(snapshot, attr, val)
                extracted[attr] = val
                feedback_notes.append(f"{res.capitalize()} stockpile set to {val}")

        # 6. Match Villager Allocations
        # e.g. "48 villagers", "14 on food", "26 on wood", "6 on gold", "2 on stone"
        total_vills_match = re.search(r"(\d+)\s*(?:total\s+)?(?:villagers|vills|workers|eco)", raw_lower)
        if total_vills_match:
            t_vills = int(total_vills_match.group(1))
            snapshot.vills_total = t_vills
            extracted["vills_total"] = t_vills
            feedback_notes.append(f"Total villagers set to {t_vills}")

        for res, attr in [("food", "vills_food"), ("wood", "vills_wood"), ("gold", "vills_gold"), ("stone", "vills_stone")]:
            m = re.search(rf"(\d+)\s*(?:vills|villagers|on|farmers|choppers|miners)?\s*(?:on|gathering|mining|chopping)?\s*{res}\b", raw_lower)
            if not m:
                m = re.search(rf"{res}\s*(?:vills|villagers|allocation)?\s*(\d+)", raw_lower)
            if m:
                val = int(m.group(1))
                setattr(snapshot, attr, val)
                extracted[attr] = val
                feedback_notes.append(f"{res.capitalize()} villagers set to {val}")

        # 7. Sighted Enemy Units
        # e.g., "spotted 5 Berserkers", "see 10 archers", "enemy has 4 knights", "sighted a castle"
        sighted_units: Dict[str, int] = dict(snapshot.sighted_enemy_units)
        for alias, unit_name in UNIT_ALIASES.items():
            # Match patterns like: "5 berserkers", "saw 5 berserk", "spotted five knights"
            pattern = rf"(?:spotted|saw|seen|sighted|enemy has|facing)?\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty)?\s*{re.escape(alias)}\b"
            for match in re.finditer(pattern, raw_lower):
                num_str = match.group(1) or "1"
                count = parse_number_expression(num_str) or 1
                sighted_units[unit_name] = sighted_units.get(unit_name, 0) + count
                extracted.setdefault("sighted_units", {})[unit_name] = sighted_units[unit_name]
                feedback_notes.append(f"Spotted {count} {unit_name}")

        snapshot.sighted_enemy_units = sighted_units

        # 8. Sighted Enemy Buildings
        sighted_buildings: Dict[str, int] = dict(snapshot.sighted_enemy_buildings)
        for alias, bldg_name in BUILDING_ALIASES.items():
            pattern = rf"(?:spotted|saw|seen|sighted|enemy has|built|dropped)?\s*(\d+|one|two|three|four|five|a|an)?\s*{re.escape(alias)}\b"
            for match in re.finditer(pattern, raw_lower):
                num_str = match.group(1) or "1"
                count = parse_number_expression(num_str) or 1
                # Filter out player's own statements like "I have 2 stables"
                start_pos = match.start()
                preceding_text = raw_lower[max(0, start_pos - 20):start_pos]
                if "i have" in preceding_text or "my" in preceding_text or "i built" in preceding_text:
                    snapshot.player_buildings[bldg_name] = snapshot.player_buildings.get(bldg_name, 0) + count
                    extracted.setdefault("player_buildings", {})[bldg_name] = snapshot.player_buildings[bldg_name]
                    feedback_notes.append(f"Player building: {count} {bldg_name}")
                else:
                    sighted_buildings[bldg_name] = sighted_buildings.get(bldg_name, 0) + count
                    extracted.setdefault("sighted_buildings", {})[bldg_name] = sighted_buildings[bldg_name]
                    feedback_notes.append(f"Spotted building: {count} {bldg_name}")

        snapshot.sighted_enemy_buildings = sighted_buildings

        # Calculate confidence
        fields_found = len(extracted)
        confidence = min(1.0, round(0.4 + (fields_found * 0.12), 2)) if fields_found > 0 else 0.2

        feedback = "; ".join(feedback_notes) if feedback_notes else "Could not extract specific match parameters from speech."

        return VoiceParseResponse(
            parsed_snapshot=snapshot,
            extracted_entities=extracted,
            confidence_score=confidence,
            feedback_message=feedback,
        )
