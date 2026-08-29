/**
 * AoE2 Dynamic Asset Database Client
 *
 * Provides typed, optimized access to unit, building, and tech image assets
 * and availability metadata across all 59 civilizations.
 */

export type AssetCategory = "unit" | "building" | "tech";

export interface AssetItem {
  name: string;
  image: string;
  available?: boolean;
  age_id?: number;
  picture_index?: number;
  node_id?: number;
}

export interface CivAssetCatalog {
  unit: Record<string, AssetItem>;
  building: Record<string, AssetItem>;
  tech: Record<string, AssetItem>;
}

export type AssetDatabase = Record<string, CivAssetCatalog>;

export interface CivGridEntity {
  name: string;
  category: "military" | "economy" | "building";
  type: "unit" | "building";
  image: string;
  age_id?: number;
  picture_index?: number;
  available?: boolean;
}

// In-memory cache for dynamic fetching
let cachedDb: AssetDatabase | null = null;

/**
 * Normalizes input name or key to lowercase snake_case for catalog lookups.
 */
export function normalizeAssetKey(text: string): string {
  if (!text) return "";
  return text
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[\(\)\?\/]+/g, " ")
    .replace(/['"’]+/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .toLowerCase();
}

/**
 * Known Civ Aliases for database lookups
 */
const KNOWN_CIV_ALIASES: Record<string, string> = {
  magyars: "magyar",
  hindustanis: "indians",
};

/**
 * Normalizes civilization name to catalog key.
 */
export function normalizeCivKey(civName?: string): string {
  if (!civName) return "_all";
  const clean = normalizeAssetKey(civName);
  return KNOWN_CIV_ALIASES[clean] || clean;
}

/**
 * Economy unit name set for classification
 */
const ECO_UNIT_NAMES = new Set([
  "villager",
  "female villager",
  "trade cart",
  "fishing ship",
  "transport ship",
  "trade cog",
  "mule cart",
  "ox cart",
]);

/**
 * Determines whether a unit belongs to the economy category.
 */
export function isEconomyUnit(name: string): boolean {
  return ECO_UNIT_NAMES.has(name.toLowerCase().trim());
}

/**
 * Known Civ Emblem mappings for civ_techtree_buttons
 */
const KNOWN_CIV_EMBLEMS: Record<string, string> = {
  berbers: "berber",
  berber: "berber",
  magyar: "magyars",
  magyars: "magyars",
  hindustanis: "indians",
  indians: "indians",
  incas: "inca",
  inca: "inca",
};

/**
 * Resolves civilization emblem PNG path from civ_techtree_buttons.
 */
export function getCivEmblemUrl(civName: string): string {
  if (!civName) return "/aoe2_assets/icons/civ_techtree_buttons/menu_techtree_franks.png";
  const clean = civName.toLowerCase().trim().replace(/[^a-z0-9]/g, "");
  const civKey = KNOWN_CIV_EMBLEMS[clean] || clean;
  return `/aoe2_assets/icons/civ_techtree_buttons/menu_techtree_${civKey}.png`;
}

/**
 * Resolves game age icon PNG path (1 = Dark, 2 = Feudal, 3 = Castle, 4 = Imperial).
 */
export function getAgeIconUrl(age: number): string {
  const clampedAge = Math.max(1, Math.min(4, Math.floor(age || 1)));
  return `/aoe2_assets/icons/age-${clampedAge}.png`;
}

/**
 * Resolves resource icon PNG path.
 */
export function getResourceIconUrl(
  resource: "food" | "wood" | "gold" | "stone" | "idle"
): string {
  switch (resource) {
    case "food":
      return "/aoe2_assets/icons/resource_food.png";
    case "wood":
      return "/aoe2_assets/icons/resource_wood.png";
    case "gold":
      return "/aoe2_assets/icons/resource_gold.png";
    case "stone":
      return "/aoe2_assets/icons/resource_stone.png";
    case "idle":
      return "/aoe2_assets/icons/idle-villager_normal.png";
    default:
      return "/aoe2_assets/icons/resource_food.png";
  }
}

/**
 * Fetches and caches the complete asset database from `/aoe2_assets/assets_db.json`.
 */
export async function getAssetDatabase(): Promise<AssetDatabase> {
  if (cachedDb) {
    return cachedDb;
  }

  try {
    const res = await fetch("/aoe2_assets/assets_db.json");
    if (!res.ok) {
      throw new Error(`Failed to load asset database: HTTP ${res.status}`);
    }
    cachedDb = (await res.json()) as AssetDatabase;
    return cachedDb;
  } catch (error) {
    console.error("Error loading AoE2 asset database:", error);
    return {};
  }
}

/**
 * Synchronous cache initializer.
 */
export function setAssetDatabaseCache(db: AssetDatabase): void {
  cachedDb = db;
}

/**
 * Retrieve an asset object for a specific civilization or fallback to global catalog.
 */
export function getAssetFromCatalog(
  db: AssetDatabase,
  nameOrKey: string,
  category: AssetCategory = "unit",
  civ?: string
): AssetItem | null {
  if (!db || Object.keys(db).length === 0) return null;
  const key = normalizeAssetKey(nameOrKey);
  const civKey = civ ? normalizeCivKey(civ) : "_all";

  // 1. Try specified civilization
  if (civKey && db[civKey]?.[category]?.[key]) {
    return db[civKey][category][key];
  }

  // 2. Fallback to global '_all' catalog
  if (db["_all"]?.[category]?.[key]) {
    return db["_all"][category][key];
  }

  // 3. Search across all categories in the civ
  if (civKey && db[civKey]) {
    for (const cat of ["unit", "building", "tech"] as AssetCategory[]) {
      if (db[civKey][cat]?.[key]) {
        return db[civKey][cat][key];
      }
    }
  }

  // 4. Search across all categories in global '_all'
  if (db["_all"]) {
    for (const cat of ["unit", "building", "tech"] as AssetCategory[]) {
      if (db["_all"][cat]?.[key]) {
        return db["_all"][cat][key];
      }
    }
  }

  // 5. Broad search across any civ
  for (const cKey of Object.keys(db)) {
    if (db[cKey]?.[category]?.[key]) {
      return db[cKey][category][key];
    }
  }

  return null;
}

/**
 * Get unit image path dynamically.
 */
export function getUnitImageUrl(
  db: AssetDatabase,
  unitName: string,
  civ?: string
): string | null {
  const asset = getAssetFromCatalog(db, unitName, "unit", civ);
  return asset?.image ?? null;
}

/**
 * Get building image path dynamically.
 */
export function getBuildingImageUrl(
  db: AssetDatabase,
  buildingName: string,
  civ?: string
): string | null {
  const asset = getAssetFromCatalog(db, buildingName, "building", civ);
  return asset?.image ?? null;
}

/**
 * Get tech image path dynamically.
 */
export function getTechImageUrl(
  db: AssetDatabase,
  techName: string,
  civ?: string
): string | null {
  const asset = getAssetFromCatalog(db, techName, "tech", civ);
  return asset?.image ?? null;
}

/**
 * Check if a unit, building, or tech is available to a given civilization.
 */
export function isCivAssetAvailable(
  db: AssetDatabase,
  nameOrKey: string,
  civ: string,
  category: AssetCategory = "unit"
): boolean {
  const asset = getAssetFromCatalog(db, nameOrKey, category, civ);
  return asset?.available ?? false;
}

/**
 * Extracts all available units and buildings for a specific civilization from the asset database.
 */
export function getCivEntities(
  db: AssetDatabase,
  civName: string
): CivGridEntity[] {
  if (!db || Object.keys(db).length === 0) return [];
  const civKey = normalizeCivKey(civName);
  const civCatalog = db[civKey] || db["_all"];
  if (!civCatalog) return [];

  const units: CivGridEntity[] = Object.values(civCatalog.unit || {})
    .filter((u) => u.available !== false)
    .map((u) => ({
      name: u.name,
      category: isEconomyUnit(u.name) ? "economy" : "military",
      type: "unit",
      image: u.image,
      age_id: u.age_id,
      picture_index: u.picture_index,
      available: u.available,
    }));

  const buildings: CivGridEntity[] = Object.values(civCatalog.building || {})
    .filter((b) => b.available !== false)
    .map((b) => ({
      name: b.name,
      category: "building",
      type: "building",
      image: b.image,
      age_id: b.age_id,
      picture_index: b.picture_index,
      available: b.available,
    }));

  return [...units, ...buildings];
}


