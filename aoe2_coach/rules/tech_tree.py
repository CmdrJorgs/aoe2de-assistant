"""
AoE2: Definitive Edition Complete Civilization & Tech Tree Definitions.

Encodes all 45+ civilizations, unique units, unique techs, team bonuses,
civ bonuses, tech trees, and disabled unit/tech graphs.
"""

from typing import Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field
from aoe2_coach.schemas.game_constants import Age, CIVILIZATIONS, CIV_NAME_TO_ID
from aoe2_coach.rules.units import ResourceCost


class Tech(BaseModel):
    id: str
    name: str
    age: Age
    research_building: str
    research_time_sec: float
    cost: ResourceCost
    prerequisites: List[str] = Field(default_factory=list)
    description: str = ""
    is_unique: bool = False
    civ: Optional[str] = None


class CivInfo(BaseModel):
    id: int
    name: str
    architecture: str
    unique_units: List[str] = Field(default_factory=list)
    castle_unique_tech: Optional[str] = None
    imperial_unique_tech: Optional[str] = None
    civ_bonuses: List[str] = Field(default_factory=list)
    team_bonus: str = ""
    disabled_units: Set[str] = Field(default_factory=set)
    disabled_techs: Set[str] = Field(default_factory=set)
    disabled_buildings: Set[str] = Field(default_factory=set)


# -------------------------------------------------------------
# Technology Catalog
# -------------------------------------------------------------
TECHS_DATABASE: Dict[str, Tech] = {
    # ------------------ Eco Techs ------------------
    "loom": Tech(id="loom", name="Loom", age=Age.DARK, research_building="town_center", research_time_sec=25.0, cost=ResourceCost(gold=50), description="+15 HP, +1/+2 armor for villagers"),
    "wheelbarrow": Tech(id="wheelbarrow", name="Wheelbarrow", age=Age.FEUDAL, research_building="town_center", research_time_sec=75.0, cost=ResourceCost(food=175, wood=50), description="Villagers move 10% faster and carry 25% more"),
    "hand_cart": Tech(id="hand_cart", name="Hand Cart", age=Age.CASTLE, research_building="town_center", research_time_sec=55.0, cost=ResourceCost(food=300, wood=200), prerequisites=["wheelbarrow"], description="Villagers move 10% faster and carry 50% more"),
    "town_watch": Tech(id="town_watch", name="Town Watch", age=Age.FEUDAL, research_building="town_center", research_time_sec=25.0, cost=ResourceCost(food=75), description="+4 LOS for all buildings"),
    "town_patrol": Tech(id="town_patrol", name="Town Patrol", age=Age.CASTLE, research_building="town_center", research_time_sec=40.0, cost=ResourceCost(food=300, gold=100), prerequisites=["town_watch"], description="+4 LOS for all buildings"),
    "double_bit_axe": Tech(id="double_bit_axe", name="Double-Bit Axe", age=Age.FEUDAL, research_building="lumber_camp", research_time_sec=25.0, cost=ResourceCost(food=100, wood=50), description="Villagers chop wood 20% faster"),
    "bow_saw": Tech(id="bow_saw", name="Bow Saw", age=Age.CASTLE, research_building="lumber_camp", research_time_sec=50.0, cost=ResourceCost(food=150, wood=100), prerequisites=["double_bit_axe"], description="Villagers chop wood 20% faster"),
    "two_man_saw": Tech(id="two_man_saw", name="Two-Man Saw", age=Age.IMPERIAL, research_building="lumber_camp", research_time_sec=100.0, cost=ResourceCost(food=300, wood=200), prerequisites=["bow_saw"], description="Villagers chop wood 10% faster"),
    "horse_collar": Tech(id="horse_collar", name="Horse Collar", age=Age.FEUDAL, research_building="mill", research_time_sec=20.0, cost=ResourceCost(food=75, wood=75), description="+75 farm food capacity"),
    "heavy_plow": Tech(id="heavy_plow", name="Heavy Plow", age=Age.CASTLE, research_building="mill", research_time_sec=40.0, cost=ResourceCost(food=125, wood=125), prerequisites=["horse_collar"], description="+125 farm food capacity"),
    "crop_rotation": Tech(id="crop_rotation", name="Crop Rotation", age=Age.IMPERIAL, research_building="mill", research_time_sec=70.0, cost=ResourceCost(food=250, wood=250), prerequisites=["heavy_plow"], description="+175 farm food capacity"),
    "gold_mining": Tech(id="gold_mining", name="Gold Mining", age=Age.FEUDAL, research_building="mining_camp", research_time_sec=30.0, cost=ResourceCost(food=100, wood=75), description="Villagers mine gold 15% faster"),
    "gold_shaft_mining": Tech(id="gold_shaft_mining", name="Gold Shaft Mining", age=Age.CASTLE, research_building="mining_camp", research_time_sec=75.0, cost=ResourceCost(food=200, wood=150), prerequisites=["gold_mining"], description="Villagers mine gold 15% faster"),
    "stone_mining": Tech(id="stone_mining", name="Stone Mining", age=Age.FEUDAL, research_building="mining_camp", research_time_sec=30.0, cost=ResourceCost(food=100, wood=75), description="Villagers mine stone 15% faster"),
    "stone_shaft_mining": Tech(id="stone_shaft_mining", name="Stone Shaft Mining", age=Age.CASTLE, research_building="mining_camp", research_time_sec=75.0, cost=ResourceCost(food=200, wood=150), prerequisites=["stone_mining"], description="Villagers mine stone 15% faster"),

    # ------------------ Blacksmith Techs ------------------
    "forging": Tech(id="forging", name="Forging", age=Age.FEUDAL, research_building="blacksmith", research_time_sec=50.0, cost=ResourceCost(food=150), description="+1 attack for infantry and cavalry"),
    "iron_casting": Tech(id="iron_casting", name="Iron Casting", age=Age.CASTLE, research_building="blacksmith", research_time_sec=75.0, cost=ResourceCost(food=220, gold=120), prerequisites=["forging"], description="+1 attack for infantry and cavalry"),
    "blast_furnace": Tech(id="blast_furnace", name="Blast Furnace", age=Age.IMPERIAL, research_building="blacksmith", research_time_sec=100.0, cost=ResourceCost(food=275, gold=225), prerequisites=["iron_casting"], description="+2 attack for infantry and cavalry"),
    "scale_mail_armor": Tech(id="scale_mail_armor", name="Scale Mail Armor", age=Age.FEUDAL, research_building="blacksmith", research_time_sec=40.0, cost=ResourceCost(food=100), description="+1/+1 armor for infantry"),
    "chain_mail_armor": Tech(id="chain_mail_armor", name="Chain Mail Armor", age=Age.CASTLE, research_building="blacksmith", research_time_sec=55.0, cost=ResourceCost(food=200, gold=100), prerequisites=["scale_mail_armor"], description="+1/+1 armor for infantry"),
    "plate_mail_armor": Tech(id="plate_mail_armor", name="Plate Mail Armor", age=Age.IMPERIAL, research_building="blacksmith", research_time_sec=70.0, cost=ResourceCost(food=300, gold=150), prerequisites=["chain_mail_armor"], description="+1/+2 armor for infantry"),
    "scale_barding_armor": Tech(id="scale_barding_armor", name="Scale Barding Armor", age=Age.FEUDAL, research_building="blacksmith", research_time_sec=45.0, cost=ResourceCost(food=150), description="+1/+1 armor for cavalry"),
    "chain_barding_armor": Tech(id="chain_barding_armor", name="Chain Barding Armor", age=Age.CASTLE, research_building="blacksmith", research_time_sec=60.0, cost=ResourceCost(food=250, gold=150), prerequisites=["scale_barding_armor"], description="+1/+1 armor for cavalry"),
    "plate_barding_armor": Tech(id="plate_barding_armor", name="Plate Barding Armor", age=Age.IMPERIAL, research_building="blacksmith", research_time_sec=75.0, cost=ResourceCost(food=350, gold=200), prerequisites=["chain_barding_armor"], description="+1/+2 armor for cavalry"),
    "fletching": Tech(id="fletching", name="Fletching", age=Age.FEUDAL, research_building="blacksmith", research_time_sec=30.0, cost=ResourceCost(food=100, gold=50), description="+1 attack and range for archers, galleys, towers, and TCs"),
    "bodkin_arrow": Tech(id="bodkin_arrow", name="Bodkin Arrow", age=Age.CASTLE, research_building="blacksmith", research_time_sec=35.0, cost=ResourceCost(food=200, gold=100), prerequisites=["fletching"], description="+1 attack and range for archers, galleys, towers, and TCs"),
    "bracer": Tech(id="bracer", name="Bracer", age=Age.IMPERIAL, research_building="blacksmith", research_time_sec=40.0, cost=ResourceCost(food=300, gold=200), prerequisites=["bodkin_arrow"], description="+1 attack and range for archers, galleys, towers, and TCs"),
    "padded_archer_armor": Tech(id="padded_archer_armor", name="Padded Archer Armor", age=Age.FEUDAL, research_building="blacksmith", research_time_sec=40.0, cost=ResourceCost(food=100), description="+1/+1 armor for archers"),
    "leather_archer_armor": Tech(id="leather_archer_armor", name="Leather Archer Armor", age=Age.CASTLE, research_building="blacksmith", research_time_sec=55.0, cost=ResourceCost(food=150, gold=150), prerequisites=["padded_archer_armor"], description="+1/+1 armor for archers"),
    "ring_archer_armor": Tech(id="ring_archer_armor", name="Ring Archer Armor", age=Age.IMPERIAL, research_building="blacksmith", research_time_sec=70.0, cost=ResourceCost(food=250, gold=250), prerequisites=["leather_archer_armor"], description="+1/+2 armor for archers"),

    # ------------------ Military Building Techs ------------------
    "bloodlines": Tech(id="bloodlines", name="Bloodlines", age=Age.FEUDAL, research_building="stable", research_time_sec=50.0, cost=ResourceCost(food=150, gold=100), description="+20 HP for all mounted units"),
    "husbandry": Tech(id="husbandry", name="Husbandry", age=Age.CASTLE, research_building="stable", research_time_sec=40.0, cost=ResourceCost(food=150), description="Cavalry moves 10% faster"),
    "thumb_ring": Tech(id="thumb_ring", name="Thumb Ring", age=Age.CASTLE, research_building="archery_range", research_time_sec=45.0, cost=ResourceCost(food=300, wood=250), description="100% accuracy and faster fire rate for archers"),
    "parthian_tactics": Tech(id="parthian_tactics", name="Parthian Tactics", age=Age.IMPERIAL, research_building="archery_range", research_time_sec=40.0, cost=ResourceCost(food=200, gold=250), description="+1/+2 armor and +4 attack vs spearmen for cavalry archers"),
    "supplies": Tech(id="supplies", name="Supplies", age=Age.FEUDAL, research_building="barracks", research_time_sec=20.0, cost=ResourceCost(food=75, gold=75), description="Militia line costs -15 food"),
    "squires": Tech(id="squires", name="Squires", age=Age.CASTLE, research_building="barracks", research_time_sec=40.0, cost=ResourceCost(food=100), description="Infantry moves 10% faster"),
    "arson": Tech(id="arson", name="Arson", age=Age.CASTLE, research_building="barracks", research_time_sec=25.0, cost=ResourceCost(food=150, gold=50), description="Infantry +2 attack vs standard buildings"),
    "gambesons": Tech(id="gambesons", name="Gambesons", age=Age.CASTLE, research_building="barracks", research_time_sec=35.0, cost=ResourceCost(food=100, gold=100), description="Militia line +1 pierce armor"),

    # ------------------ University Techs ------------------
    "ballistics": Tech(id="ballistics", name="Ballistics", age=Age.CASTLE, research_building="university", research_time_sec=60.0, cost=ResourceCost(wood=300, gold=175), description="Ranged units and defenses lead moving targets"),
    "chemistry": Tech(id="chemistry", name="Chemistry", age=Age.IMPERIAL, research_building="university", research_time_sec=100.0, cost=ResourceCost(food=300, gold=200), description="+1 missile attack, unlocks gunpowder units"),
    "siege_engineers": Tech(id="siege_engineers", name="Siege Engineers", age=Age.IMPERIAL, research_building="university", research_time_sec=45.0, cost=ResourceCost(food=500, wood=600), description="+1 range for Onagers and Trebuchets, +20% bonus damage vs buildings"),
    "masonry": Tech(id="masonry", name="Masonry", age=Age.CASTLE, research_building="university", research_time_sec=40.0, cost=ResourceCost(wood=150, food=150), description="+10% building HP, +1/+1 armor, +3 building armor"),
    "architecture": Tech(id="architecture", name="Architecture", age=Age.IMPERIAL, research_building="university", research_time_sec=70.0, cost=ResourceCost(wood=200, food=300), prerequisites=["masonry"], description="+10% building HP, +1/+1 armor, +3 building armor"),
    "murder_holes": Tech(id="murder_holes", name="Murder Holes", age=Age.CASTLE, research_building="university", research_time_sec=35.0, cost=ResourceCost(food=200, stone=100), description="Removes minimum range for towers and castles"),
}


# -------------------------------------------------------------
# 45 Civilizations Master Database
# -------------------------------------------------------------
CIVILIZATIONS_DATABASE: Dict[str, CivInfo] = {
    "britons": CivInfo(
        id=1,
        name="Britons",
        architecture="Western European",
        unique_units=["longbowman", "elite_longbowman"],
        castle_unique_tech="yeomen",
        imperial_unique_tech="warwolf",
        civ_bonuses=[
            "Foot archers (except Skirmishers) +1/+2 range in Castle/Imperial Age",
            "Town Centers cost -50% wood starting in Castle Age",
            "Shepherds work 25% faster",
        ],
        team_bonus="Archery Ranges work 20% faster",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "hand_cannoneer", "siege_onager", "bombard_cannon", "cannon_galleon"},
        disabled_techs={"thumb_ring", "bloodlines", "parthian_tactics", "ring_archer_armor"},
    ),
    "franks": CivInfo(
        id=2,
        name="Franks",
        architecture="Western European",
        unique_units=["throwing_axeman", "elite_throwing_axeman"],
        castle_unique_tech="chivalry",
        imperial_unique_tech="bearded_axe",
        civ_bonuses=[
            "Cavalry +20% HP starting in Feudal Age",
            "Castles cost -25%",
            "Mill technologies (Horse Collar, Heavy Plow, Crop Rotation) are free",
            "Foragers work 15% faster",
        ],
        team_bonus="Knights +2 line of sight",
        disabled_units={"arbalester", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "siege_ram", "siege_onager"},
        disabled_techs={"bloodlines", "thumb_ring", "parthian_tactics", "ring_archer_armor", "bracer"},
    ),
    "goths": CivInfo(
        id=3,
        name="Goths",
        architecture="Central European",
        unique_units=["huskarl", "elite_huskarl"],
        castle_unique_tech="anarchy",
        imperial_unique_tech="perfusion",
        civ_bonuses=[
            "Infantry cost -20% in Dark, -25% in Feudal, -30% in Castle, -35% in Imperial Age",
            "Infantry have +1 attack bonus vs standard buildings per age starting in Feudal Age",
            "Villagers have +5 attack vs wild boar and carry +15 meat",
            "+10 population cap in Imperial Age",
        ],
        team_bonus="Barracks work 20% faster",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "arbalester", "siege_onager", "siege_ram"},
        disabled_techs={"plate_barding_armor", "ring_archer_armor", "supplies", "guard_tower_tech", "keep_tech"},
        disabled_buildings={"stone_wall", "gate", "guard_tower", "keep"},
    ),
    "teutons": CivInfo(
        id=4,
        name="Teutons",
        architecture="Central European",
        unique_units=["teutonic_knight", "elite_teutonic_knight"],
        castle_unique_tech="ironclad",
        imperial_unique_tech="crenellations",
        civ_bonuses=[
            "Barracks and Stable units gain +1/+2 melee armor in Castle/Imperial Age",
            "Farms cost -40%",
            "Town Centers can garrison +10 units and fire +5 arrows",
            "Monks heal from 2x range",
        ],
        team_bonus="Units resist monk conversion",
        disabled_units={"light_cavalry", "hussar", "camel_rider", "heavy_camel_rider", "arbalester", "siege_ram"},
        disabled_techs={"husbandry", "thumb_ring", "parthian_tactics", "bracer", "dry_dock"},
    ),
    "japanese": CivInfo(
        id=5,
        name="Japanese",
        architecture="East Asian",
        unique_units=["samurai", "elite_samurai"],
        castle_unique_tech="yasama",
        imperial_unique_tech="kataparuto",
        civ_bonuses=[
            "Infantry attack 33% faster starting in Feudal Age",
            "Lumber Camps, Mining Camps, and Mills cost -50% wood",
            "Fishing Ships have 2x HP, +2 pierce armor, and work 5%/10%/15%/20% faster per age",
        ],
        team_bonus="Galleys have +50% line of sight",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "siege_ram", "siege_onager", "bombard_cannon"},
        disabled_techs={"plate_barding_armor", "bloodlines", "husbandry"},
    ),
    "chinese": CivInfo(
        id=6,
        name="Chinese",
        architecture="East Asian",
        unique_units=["chu_ko_nu", "elite_chu_ko_nu"],
        castle_unique_tech="great_wall",
        imperial_unique_tech="rocketry",
        civ_bonuses=[
            "Start game with +3 villagers, -50 wood, -200 food",
            "Technologies cost -10%/-15%/-20% in Feudal/Castle/Imperial Age",
            "Town Centers support 10 population and have +5 line of sight",
            "Demolition Ships have +50% HP",
        ],
        team_bonus="Farms provide +45 food",
        disabled_units={"paladin", "hussar", "hand_cannoneer", "siege_onager", "bombard_cannon"},
        disabled_techs={"parthian_tactics", "supplies", "siege_engineers"},
    ),
    "byzantines": CivInfo(
        id=7,
        name="Byzantines",
        architecture="Mediterranean",
        unique_units=["cataphract", "elite_cataphract"],
        castle_unique_tech="greek_fire",
        imperial_unique_tech="logistica",
        civ_bonuses=[
            "Buildings have +10%/+20%/+30%/+40% HP in Dark/Feudal/Castle/Imperial Age",
            "Spearman, Skirmisher, and Camel lines cost -25%",
            "Fire Ships attack 25% faster",
            "Imperial Age technology costs -33%",
        ],
        team_bonus="Monks heal 100% faster",
        disabled_units={"siege_onager", "heavy_scorpion"},
        disabled_techs={"bloodlines", "parthian_tactics", "blast_furnace", "masonry", "architecture"},
    ),
    "persians": CivInfo(
        id=8,
        name="Persians",
        architecture="Middle Eastern",
        unique_units=["war_elephant", "elite_war_elephant"],
        castle_unique_tech="kamandaran",
        imperial_unique_tech="citadels",
        civ_bonuses=[
            "Start with +50 food and +50 wood",
            "Town Centers and Docks have 2x HP and work 10%/15%/20% faster in Feudal/Castle/Imperial Age",
            "Knight line gains +2 attack vs archers",
        ],
        team_bonus="Knights +2 attack vs archers",
        disabled_units={"arbalester", "siege_onager"},
        disabled_techs={"bracer", "siege_engineers", "treadmill_crane"},
    ),
    "saracens": CivInfo(
        id=9,
        name="Saracens",
        architecture="Middle Eastern",
        unique_units=["mameluke", "elite_mameluke"],
        castle_unique_tech="zealotry",
        imperial_unique_tech="counterweights",
        civ_bonuses=[
            "Market commodity transaction fee is only 5%",
            "Transport Ships have 2x HP and +5 carry capacity",
            "Galleys attack 25% faster",
            "Camel units have +10 HP in Castle Age, +20 HP in Imperial Age",
            "Foot archers have +3 attack vs standard buildings",
        ],
        team_bonus="Foot archers have +2 attack vs standard buildings",
        disabled_units={"paladin", "battle_elephant"},
        disabled_techs={"guilds", "crop_rotation", "architecture"},
    ),
    "turks": CivInfo(
        id=10,
        name="Turks",
        architecture="Middle Eastern",
        unique_units=["janissary", "elite_janissary"],
        castle_unique_tech="sipahi",
        imperial_unique_tech="artillery",
        civ_bonuses=[
            "Gunpowder units have +25% HP; Chemistry is free",
            "Gold miners work 20% faster",
            "Light Cavalry and Hussar upgrades are free",
            "Scout line has +1 pierce armor",
        ],
        team_bonus="Gunpowder units created 25% faster",
        disabled_units={"arbalester", "elite_skirmisher", "imperial_skirmisher", "pikeman", "halberdier", "paladin", "onager", "siege_onager"},
        disabled_techs={"block_printing", "crop_rotation", "siege_engineers"},
    ),
    "vikings": CivInfo(
        id=11,
        name="Vikings",
        architecture="Central European",
        unique_units=["berserk", "elite_berserk"],
        castle_unique_tech="chieftains",
        imperial_unique_tech="berserkergang",
        civ_bonuses=[
            "Warships cost -15% in Feudal, -15% in Castle, -20% in Imperial Age",
            "Infantry have +20% HP starting in Feudal Age",
            "Wheelbarrow and Hand Cart are free upon reaching the respective ages",
        ],
        team_bonus="Docks cost -15%",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "hand_cannoneer", "bombard_cannon", "siege_onager"},
        disabled_techs={"bloodlines", "husbandry", "parthian_tactics", "plate_barding_armor", "stone_shaft_mining"},
    ),
    "mongols": CivInfo(
        id=12,
        name="Mongols",
        architecture="East Asian",
        unique_units=["mangudai", "elite_mangudai"],
        castle_unique_tech="nomads",
        imperial_unique_tech="drill",
        civ_bonuses=[
            "Cavalry Archers fire 25% faster",
            "Light Cavalry, Hussars, and Steppe Lancers have +30% HP",
            "Hunters work 40% faster",
        ],
        team_bonus="Scout line has +2 line of sight",
        disabled_units={"paladin", "arbalester", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"ring_archer_armor", "plate_barding_armor", "redemption", "block_printing", "architecture"},
    ),
    "celts": CivInfo(
        id=13,
        name="Celts",
        architecture="Western European",
        unique_units=["woad_raider", "elite_woad_raider"],
        castle_unique_tech="stronghold",
        imperial_unique_tech="furor_celtica",
        civ_bonuses=[
            "Infantry move 15% faster starting in Feudal Age",
            "Lumberjacks work 15% faster",
            "Siege weapons fire 25% faster",
            "Sheep cannot be converted if in Celt unit's line of sight",
        ],
        team_bonus="Siege Workshops work 20% faster",
        disabled_units={"paladin", "arbalester", "camel_rider", "heavy_camel_rider", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"bloodlines", "thumb_ring", "ring_archer_armor", "bracer", "plate_barding_armor"},
    ),
    "spanish": CivInfo(
        id=14,
        name="Spanish",
        architecture="Mediterranean",
        unique_units=["conquistador", "elite_conquistador", "missionary"],
        castle_unique_tech="inquisition",
        imperial_unique_tech="supremacy",
        civ_bonuses=[
            "Builders work 30% faster",
            "Blacksmith technologies cost no gold",
            "Cannon Galleons benefit from Ballistics",
            "Gunpowder units fire 18% faster",
        ],
        team_bonus="Trade carts generate +25% gold",
        disabled_units={"crossbowman", "arbalester", "siege_onager", "camel_rider", "heavy_camel_rider"},
        disabled_techs={"parthian_tactics", "siege_engineers", "crop_rotation"},
    ),
    "aztecs": CivInfo(
        id=15,
        name="Aztecs",
        architecture="Mesoamerican",
        unique_units=["jaguar_warrior", "elite_jaguar_warrior"],
        castle_unique_tech="atlatl",
        imperial_unique_tech="garland_wars",
        civ_bonuses=[
            "Villagers carry +3 resources",
            "Military units are created 11% faster",
            "Monks gain +5 HP for each researched Monastery technology",
            "Start with +50 gold",
        ],
        team_bonus="Relics generate +33% gold",
        disabled_units={"scout_cavalry", "light_cavalry", "hussar", "knight", "cavalier", "paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"bloodlines", "husbandry", "scale_barding_armor", "chain_barding_armor", "plate_barding_armor", "thumb_ring", "parthian_tactics", "ring_archer_armor", "masonry", "architecture"},
        disabled_buildings={"stable"},
    ),
    "mayans": CivInfo(
        id=16,
        name="Mayans",
        architecture="Mesoamerican",
        unique_units=["plumed_archer", "elite_plumed_archer"],
        castle_unique_tech="hulche_javelineers",
        imperial_unique_tech="el_dorado",
        civ_bonuses=[
            "Start with +1 villager, but -50 food",
            "Resources last 15% longer",
            "Foot archers cost -10% in Feudal, -20% in Castle, -30% in Imperial Age",
        ],
        team_bonus="Walls cost -50%",
        disabled_units={"scout_cavalry", "light_cavalry", "hussar", "knight", "cavalier", "paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "hand_cannoneer", "bombard_cannon", "siege_onager"},
        disabled_techs={"bloodlines", "husbandry", "scale_barding_armor", "chain_barding_armor", "plate_barding_armor"},
        disabled_buildings={"stable"},
    ),
    "huns": CivInfo(
        id=17,
        name="Huns",
        architecture="Central European",
        unique_units=["tarkan", "elite_tarkan"],
        castle_unique_tech="marauders",
        imperial_unique_tech="athelm_war",
        civ_bonuses=[
            "Do not need houses, but start with -100 wood",
            "Cavalry Archers cost -10% in Castle, -20% in Imperial Age",
            "Trebuchets have +30% accuracy",
        ],
        team_bonus="Stables work 20% faster",
        disabled_units={"arbalester", "hand_cannoneer", "siege_onager", "bombard_cannon"},
        disabled_techs={"ring_archer_armor", "guard_tower_tech", "keep_tech", "fortified_wall"},
        disabled_buildings={"house"},
    ),
    "koreans": CivInfo(
        id=18,
        name="Koreans",
        architecture="East Asian",
        unique_units=["war_wagon", "elite_war_wagon", "turtle_ship"],
        castle_unique_tech="eupseong",
        imperial_unique_tech="shinkichon",
        civ_bonuses=[
            "Villagers have +3 line of sight",
            "Stone miners work 20% faster",
            "Tower upgrades are free; Towers have +1/+2 range in Castle/Imperial Age",
            "Military units (except siege) cost -20% wood",
        ],
        team_bonus="Mangonel line minimum range reduced",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "demolition_ship"},
        disabled_techs={"bloodlines", "parthian_tactics", "blast_furnace"},
    ),
    "italians": CivInfo(
        id=19,
        name="Italians",
        architecture="Mediterranean",
        unique_units=["genoese_crossbowman", "elite_genoese_crossbowman", "condottiero"],
        castle_unique_tech="pavise",
        imperial_unique_tech="silk_road",
        civ_bonuses=[
            "Advancing to next Age costs -15%",
            "Dock technologies and University technologies cost -33%",
            "Fishing Ships cost -15%",
            "Gunpowder units cost -20%",
        ],
        team_bonus="Condottiero available in Imperial Age Barracks for allies",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "siege_onager"},
        disabled_techs={"parthian_tactics", "siege_engineers"},
    ),
    "hindustanis": CivInfo(
        id=20,
        name="Hindustanis",
        architecture="South Asian",
        unique_units=["ghulam", "elite_ghulam", "imperial_camel_rider"],
        castle_unique_tech="grand_trunk_road",
        imperial_unique_tech="shatagni",
        civ_bonuses=[
            "Villagers cost -10%/-15%/-20%/-25% in Dark/Feudal/Castle/Imperial Age",
            "Camel units attack 20% faster",
            "Gunpowder units have +1/+1 armor",
        ],
        team_bonus="Camel and light cavalry units have +2 attack vs buildings",
        disabled_units={"knight", "cavalier", "paladin", "arbalester", "siege_onager"},
        disabled_techs={"plate_barding_armor", "parthian_tactics"},
    ),
    "incas": CivInfo(
        id=21,
        name="Incas",
        architecture="Mesoamerican",
        unique_units=["kamayuk", "elite_kamayuk", "slinger"],
        castle_unique_tech="andean_sling",
        imperial_unique_tech="fabric_shields",
        civ_bonuses=[
            "Start game with a free Llama",
            "Villagers benefit from Blacksmith infantry armor upgrades",
            "Houses support 10 population",
            "Buildings cost -15% stone",
        ],
        team_bonus="Start with a free Llama",
        disabled_units={"scout_cavalry", "light_cavalry", "hussar", "knight", "cavalier", "paladin", "camel_rider", "heavy_camel_rider", "steppe_lancer", "battle_elephant", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"bloodlines", "husbandry", "scale_barding_armor", "chain_barding_armor", "plate_barding_armor"},
        disabled_buildings={"stable"},
    ),
    "magyars": CivInfo(
        id=22,
        name="Magyars",
        architecture="Eastern European",
        unique_units=["magyar_huszar", "elite_magyar_huszar"],
        castle_unique_tech="corvinian_army",
        imperial_unique_tech="recurve_bow",
        civ_bonuses=[
            "Forging, Iron Casting, and Blast Furnace are free upon reaching the respective ages",
            "Scout Cavalry line costs -15%",
            "Villagers kill wild predators in one strike",
        ],
        team_bonus="Foot archers have +2 line of sight",
        disabled_units={"camel_rider", "heavy_camel_rider", "hand_cannoneer", "siege_ram", "siege_onager", "bombard_cannon"},
        disabled_techs={"squires", "plate_mail_armor"},
    ),
    "slavs": CivInfo(
        id=23,
        name="Slavs",
        architecture="Eastern European",
        unique_units=["boyar", "elite_boyar"],
        castle_unique_tech="detinets",
        imperial_unique_tech="druzhina",
        civ_bonuses=[
            "Farmers work 10% faster",
            "Supplies is free",
            "Siege Workshop units cost -15%",
        ],
        team_bonus="Military buildings provide +5 population space",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "arbalester", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"thumb_ring", "parthian_tactics", "bracer"},
    ),
    "portuguese": CivInfo(
        id=24,
        name="Portuguese",
        architecture="Mediterranean",
        unique_units=["organ_gun", "elite_organ_gun", "caravel"],
        castle_unique_tech="carrack",
        imperial_unique_tech="arquebus",
        civ_bonuses=[
            "All units cost -20% gold",
            "All technologies research 30% faster",
            "Can build Feitoria in Imperial Age",
            "Ships have +10% HP",
        ],
        team_bonus="Line of sight is shared with allies from the start of the game",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "heavy_cavalry_archer", "siege_onager"},
        disabled_techs={"squires", "parthian_tactics"},
    ),
    "ethiopians": CivInfo(
        id=25,
        name="Ethiopians",
        architecture="African",
        unique_units=["shotel_warrior", "elite_shotel_warrior"],
        castle_unique_tech="royal_heirs",
        imperial_unique_tech="torsion_engines",
        civ_bonuses=[
            "Foot archers fire 18% faster",
            "Receive +100 food and +100 gold upon advancing to the next Age",
            "Pikeman upgrade is free",
        ],
        team_bonus="Towers and Outposts have +3 line of sight",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "hand_cannoneer"},
        disabled_techs={"bloodlines", "plate_barding_armor", "parthian_tactics"},
    ),
    "malians": CivInfo(
        id=26,
        name="Malians",
        architecture="African",
        unique_units=["gbeto", "elite_gbeto"],
        castle_unique_tech="tigui",
        imperial_unique_tech="farimba",
        civ_bonuses=[
            "Buildings cost -15% wood (except farms)",
            "Barracks units gain +1 pierce armor per age starting in Feudal Age",
            "Gold Mining upgrades are free",
        ],
        team_bonus="Universities research 80% faster",
        disabled_units={"paladin", "hussar", "arbalester", "siege_onager"},
        disabled_techs={"bracer", "blast_furnace", "parthian_tactics"},
    ),
    "berbers": CivInfo(
        id=27,
        name="Berbers",
        architecture="Middle Eastern",
        unique_units=["camel_archer", "elite_camel_archer", "genitour"],
        castle_unique_tech="kasbah",
        imperial_unique_tech="maghrebi_camels",
        civ_bonuses=[
            "Villagers move 10% faster",
            "Stable units cost -15% in Castle, -20% in Imperial Age",
            "Ships move 10% faster",
        ],
        team_bonus="Genitour available in Archery Range for allies",
        disabled_units={"paladin", "arbalester", "siege_onager"},
        disabled_techs={"parthian_tactics", "architecture", "siege_engineers"},
    ),
    "khmer": CivInfo(
        id=28,
        name="Khmer",
        architecture="Southeast Asian",
        unique_units=["ballista_elephant", "elite_ballista_elephant"],
        castle_unique_tech="tusk_swords",
        imperial_unique_tech="double_crossbow",
        civ_bonuses=[
            "No prerequisite buildings required to advance to the next Age or unlock buildings",
            "Farmers do not require drop-off buildings (Mills/TCs)",
            "Battle Elephants move 10% faster",
            "Villagers can garrison inside Houses",
        ],
        team_bonus="Scorpions have +1 range",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "champion", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"supplies", "thumb_ring", "plate_mail_armor"},
    ),
    "malay": CivInfo(
        id=29,
        name="Malay",
        architecture="Southeast Asian",
        unique_units=["karambit_warrior", "elite_karambit_warrior"],
        castle_unique_tech="thalassocracy",
        imperial_unique_tech="forced_levy",
        civ_bonuses=[
            "Advance to the next Age 66% faster",
            "Fish Traps cost -33% and provide infinite food",
            "Battle Elephants cost -30% in Castle, -40% in Imperial Age",
        ],
        team_bonus="Docks provide +100% line of sight",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "hand_cannoneer", "siege_onager"},
        disabled_techs={"bloodlines", "chain_barding_armor", "plate_barding_armor", "parthian_tactics"},
    ),
    "burmese": CivInfo(
        id=30,
        name="Burmese",
        architecture="Southeast Asian",
        unique_units=["arambai", "elite_arambai"],
        castle_unique_tech="howdah",
        imperial_unique_tech="manipur_cavalry",
        civ_bonuses=[
            "Lumber Camp technologies are free",
            "Infantry have +1 attack per age starting in Feudal Age",
            "Monastery technologies cost -50%",
        ],
        team_bonus="Relics are visible on the map from the start of the game",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "arbalester", "hand_cannoneer", "siege_onager"},
        disabled_techs={"leather_archer_armor", "ring_archer_armor", "thumb_ring", "heresy"},
    ),
    "vietnamese": CivInfo(
        id=31,
        name="Vietnamese",
        architecture="Southeast Asian",
        unique_units=["rattan_archer", "elite_rattan_archer", "imperial_skirmisher"],
        castle_unique_tech="chatras",
        imperial_unique_tech="paper_money",
        civ_bonuses=[
            "Reveal enemy positions at the game start",
            "Archery Range units have +20% HP",
            "Economic upgrades cost no wood",
        ],
        team_bonus="Imperial Skirmisher upgrade available in Imperial Age",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "hand_cannoneer", "siege_onager"},
        disabled_techs={"parthian_tactics", "blast_furnace", "masonry", "architecture"},
    ),
    "bulgarians": CivInfo(
        id=32,
        name="Bulgarians",
        architecture="Eastern European",
        unique_units=["konnik", "elite_konnik"],
        castle_unique_tech="stirrups",
        imperial_unique_tech="bagains",
        civ_bonuses=[
            "Militia line upgrades are free",
            "Town Centers cost -50% stone",
            "Blacksmith and Siege Workshop technologies cost -50% food",
            "Can build Krepost (mini-castle)",
        ],
        team_bonus="Blacksmiths work 80% faster",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "crossbowman", "arbalester", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"ring_archer_armor", "plate_mail_armor", "fortified_wall"},
    ),
    "tatars": CivInfo(
        id=33,
        name="Tatars",
        architecture="Central Asian",
        unique_units=["keshik", "elite_keshik", "flaming_camel"],
        castle_unique_tech="silk_armor",
        imperial_unique_tech="timurid_siegecraft",
        civ_bonuses=[
            "Units deal +50% damage when fighting from higher elevation (standard is +25%)",
            "Thumb Ring and Parthian Tactics are free",
            "Herdables contain +50% food",
            "Receive +2 sheep when building a Town Center in Castle and Imperial Age",
        ],
        team_bonus="Cavalry Archers have +2 line of sight",
        disabled_units={"paladin", "arbalester", "hand_cannoneer", "bombard_cannon", "siege_onager"},
        disabled_techs={"chain_mail_armor", "plate_mail_armor", "architecture"},
    ),
    "cumans": CivInfo(
        id=34,
        name="Cumans",
        architecture="Central Asian",
        unique_units=["kipchak", "elite_kipchak"],
        castle_unique_tech="steppe_husbandry",
        imperial_unique_tech="cuman_mercenaries",
        civ_bonuses=[
            "Can build an additional Town Center and Siege Workshop in Feudal Age",
            "Cavalry move 5%/10%/15% faster in Feudal/Castle/Imperial Age",
            "Archery Ranges and Stables cost -75 wood",
        ],
        team_bonus="Palisade Walls have +33% HP",
        disabled_units={"arbalester", "hand_cannoneer", "bombard_cannon", "heavy_camel_rider"},
        disabled_techs={"bracer", "husbandry", "stone_shaft_mining"},
    ),
    "lithuanians": CivInfo(
        id=35,
        name="Lithuanians",
        architecture="Eastern European",
        unique_units=["leitis", "elite_leitis"],
        castle_unique_tech="hill_forts",
        imperial_unique_tech="tower_shields",
        civ_bonuses=[
            "Start with +150 food",
            "Spearman and Skirmisher lines move 10% faster",
            "Each garrisoned Relic gives Knights and Leitis +1 attack (max +4)",
        ],
        team_bonus="Monasteries work 20% faster",
        disabled_units={"arbalester", "siege_onager", "heavy_camel_rider"},
        disabled_techs={"parthian_tactics", "siege_engineers", "arrowslits"},
    ),
    "burgundians": CivInfo(
        id=36,
        name="Burgundians",
        architecture="Western European",
        unique_units=["coustillier", "elite_coustillier"],
        castle_unique_tech="burgundian_vineyards",
        imperial_unique_tech="flemish_revolution",
        civ_bonuses=[
            "Economic upgrades available one Age earlier, and cost -33% food",
            "Stable technologies cost -50%",
            "Cavalier upgrade available in Castle Age",
            "Gunpowder units gain +25% attack",
        ],
        team_bonus="Relics generate both gold and food",
        disabled_units={"arbalester", "heavy_camel_rider", "siege_onager", "steppe_lancer"},
        disabled_techs={"bloodlines", "thumb_ring", "ring_archer_armor", "supplies"},
    ),
    "sicilians": CivInfo(
        id=37,
        name="Sicilians",
        architecture="Mediterranean",
        unique_units=["serjeant", "elite_serjeant"],
        castle_unique_tech="first_crusade",
        imperial_unique_tech="hauberk",
        civ_bonuses=[
            "Land military units absorb 33% of all incoming bonus damage",
            "Castles and Town Centers built 100% faster",
            "Farm upgrades provide +100% additional food",
            "Can build Donjon",
        ],
        team_bonus="Transport Ships have +5 carry capacity and +10 armor vs bonus attacks",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "hand_cannoneer", "bombard_cannon", "siege_onager"},
        disabled_techs={"ring_archer_armor", "thumb_ring", "parthian_tactics"},
    ),
    "poles": CivInfo(
        id=38,
        name="Poles",
        architecture="Eastern European",
        unique_units=["obuch", "elite_obuch"],
        castle_unique_tech="szlachta_privileges",
        imperial_unique_tech="lechitic_legacy",
        civ_bonuses=[
            "Villagers regenerate 5/10/15/20 HP per minute per age",
            "Folwark replaces Mill and collects 10% food instantly when farms are placed around it",
            "Stone miners generate gold in addition to stone (2 stone = 1 gold)",
        ],
        team_bonus="Scout cavalry line +1 attack vs archers",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "hand_cannoneer", "siege_onager"},
        disabled_techs={"ring_archer_armor", "plate_barding_armor", "parthian_tactics"},
    ),
    "bohemians": CivInfo(
        id=39,
        name="Bohemians",
        architecture="Central European",
        unique_units=["hussite_wagon", "elite_hussite_wagon", "houfnice"],
        castle_unique_tech="wagenburg_tactics",
        imperial_unique_tech="hussite_reforms",
        civ_bonuses=[
            "Blacksmith and University technologies cost no wood",
            "Chemistry and Hand Cannoneers available in Castle Age",
            "Spearman line deals +25% bonus damage",
            "Mining Camp technologies are free",
        ],
        team_bonus="Markets work 80% faster",
        disabled_units={"paladin", "hussar", "camel_rider", "heavy_camel_rider", "steppe_lancer", "siege_onager"},
        disabled_techs={"bloodlines", "thumb_ring", "parthian_tactics", "plate_barding_armor"},
    ),
    "dravidians": CivInfo(
        id=40,
        name="Dravidians",
        architecture="South Asian",
        unique_units=["urumi_swordsman", "elite_urumi_swordsman", "thirisadai"],
        castle_unique_tech="medical_corps",
        imperial_unique_tech="wootz_steel",
        civ_bonuses=[
            "Receive +200 wood upon advancing to the next Age",
            "Fishermen and Fishing Ships carry +15 food",
            "Barracks technologies cost -50%",
            "Skirmishers and Elephant Archers attack 25% faster",
        ],
        team_bonus="Docks provide +5 population space",
        disabled_units={"knight", "cavalier", "paladin", "camel_rider", "heavy_camel_rider", "hussar", "siege_onager"},
        disabled_techs={"bloodlines", "husbandry", "plate_barding_armor"},
    ),
    "bengalis": CivInfo(
        id=41,
        name="Bengalis",
        architecture="South Asian",
        unique_units=["ratha", "elite_ratha"],
        castle_unique_tech="paiks",
        imperial_unique_tech="mahayana",
        civ_bonuses=[
            "Receive +2 villagers upon advancing to the next Age",
            "Elephant units receive 25% less bonus damage and resist conversion",
            "Ships regenerate 15 HP per minute",
        ],
        team_bonus="Trade units generate 10% food in addition to gold",
        disabled_units={"knight", "cavalier", "paladin", "camel_rider", "heavy_camel_rider", "hussar", "bombard_cannon"},
        disabled_techs={"plate_barding_armor", "thumb_ring", "heresy"},
    ),
    "gurjaras": CivInfo(
        id=42,
        name="Gurjaras",
        architecture="South Asian",
        unique_units=["chakram_thrower", "elite_chakram_thrower", "shrivamsha_rider", "elite_shrivamsha_rider"],
        castle_unique_tech="kshatriyas",
        imperial_unique_tech="frontier_guards",
        civ_bonuses=[
            "Can garrison herdables in Mills to continuously produce food",
            "Mounted units deal +20%/+30%/+40% bonus damage in Feudal/Castle/Imperial Age",
            "Can garrison Fishing Ships in Docks",
        ],
        team_bonus="Camel and elephant units created 25% faster",
        disabled_units={"knight", "cavalier", "paladin", "arbalester", "siege_onager"},
        disabled_techs={"blast_furnace", "plate_barding_armor", "parthian_tactics", "supplies"},
    ),
    "romans": CivInfo(
        id=43,
        name="Romans",
        architecture="Mediterranean",
        unique_units=["centurion", "elite_centurion", "legionary"],
        castle_unique_tech="ballistas",
        imperial_unique_tech="comitatenses",
        civ_bonuses=[
            "Villagers work 5% faster",
            "Infantry receive 2x effect from Blacksmith armor upgrades",
            "Galleys fire 2 projectiles",
            "Scorpions cost -60% gold and benefit from Ballistics",
        ],
        team_bonus="Scorpions minimum range reduced",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "arbalester", "hand_cannoneer", "bombard_cannon", "siege_onager"},
        disabled_techs={"thumb_ring", "parthian_tactics", "bracer", "supplies"},
    ),
    "armenians": CivInfo(
        id=44,
        name="Armenians",
        architecture="Caucasian",
        unique_units=["composite_bowman", "elite_composite_bowman"],
        castle_unique_tech="cilician_fleet",
        imperial_unique_tech="fereters",
        civ_bonuses=[
            "Mule Carts cost -25% and Mule Cart technologies are 25% more effective",
            "First Fortified Church receives a free Relic",
            "Infantry upgrades (except Spear line) available one age earlier",
            "Galley line fires 2 additional projectiles",
        ],
        team_bonus="Infantry have +2 line of sight",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "arbalester", "hand_cannoneer", "siege_onager", "bombard_cannon"},
        disabled_techs={"plate_barding_armor", "thumb_ring", "parthian_tactics"},
    ),
    "georgians": CivInfo(
        id=45,
        name="Georgians",
        architecture="Caucasian",
        unique_units=["monaspa", "elite_monaspa"],
        castle_unique_tech="svan_towers",
        imperial_unique_tech="aznauri_cavalry",
        civ_bonuses=[
            "Start with -50 food, but with a Mule Cart",
            "Units take -15% damage when fighting from higher elevation (standard is +25% attack / -25% defense)",
            "Cavalry regenerate 5/10/15 HP per minute in Feudal/Castle/Imperial Age",
            "Buildings regenerate 10% HP per minute",
        ],
        team_bonus="Repairing buildings costs -25% resources",
        disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "arbalester", "hand_cannoneer", "bombard_cannon"},
        disabled_techs={"ring_archer_armor", "thumb_ring", "parthian_tactics"},
    ),
}


# -------------------------------------------------------------
# Query & Validation Functions
# -------------------------------------------------------------
def get_civ_info(civ: Union[str, int]) -> Optional[CivInfo]:
    """Retrieve full civilization information by ID or canonical name."""
    if isinstance(civ, int):
        civ_name = CIVILIZATIONS.get(civ, "").lower()
    else:
        civ_name = civ.lower()
    return CIVILIZATIONS_DATABASE.get(civ_name)


def is_unit_available(civ: Union[str, int], unit_id: str, age: Optional[Age] = None) -> bool:
    """Check if a unit is available to a given civilization at an optional age."""
    info = get_civ_info(civ)
    if not info:
        return True
    
    unit_id_clean = unit_id.lower()
    if unit_id_clean in info.disabled_units:
        return False
        
    return True


def is_tech_available(civ: Union[str, int], tech_id: str, age: Optional[Age] = None) -> bool:
    """Check if a technology is available to a given civilization."""
    info = get_civ_info(civ)
    if not info:
        return True
        
    tech_id_clean = tech_id.lower()
    if tech_id_clean in info.disabled_techs:
        return False
        
    return True


def is_building_available(civ: Union[str, int], building_id: str) -> bool:
    """Check if a building is constructible by a given civilization."""
    info = get_civ_info(civ)
    if not info:
        return True
        
    b_clean = building_id.lower()
    if b_clean in info.disabled_buildings:
        return False
        
    return True


def get_all_civs() -> List[CivInfo]:
    """Return list of all 45 civilizations."""
    return list(CIVILIZATIONS_DATABASE.values())
