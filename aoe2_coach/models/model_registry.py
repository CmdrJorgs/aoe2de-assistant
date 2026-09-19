"""
AoE2 Versioned ML Inference Model Registry.
Maintains isolated MLInferenceService instances for each supported game patch version.
"""

from typing import Dict, Optional, List
import logging
from aoe2_coach.rules.game_ruleset import RulesRegistry
from aoe2_coach.models.inference_service import MLInferenceService

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Singleton registry managing isolated MLInferenceService sessions per patch version.
    """
    _services: Dict[str, MLInferenceService] = {}

    @classmethod
    def get_service(cls, patch_version: Optional[str] = "latest") -> MLInferenceService:
        """
        Retrieve or instantiate an MLInferenceService strictly scoped to the specified patch version.
        """
        ruleset = RulesRegistry.get(patch_version)
        v_key = ruleset.patch_version.strip().lower()

        if v_key not in cls._services:
            logger.info(f"Initializing versioned MLInferenceService for patch: {v_key} ({ruleset.display_name})")
            cls._services[v_key] = MLInferenceService(
                ruleset=ruleset,
                patch_version=v_key,
            )

        return cls._services[v_key]

    @classmethod
    def clear(cls) -> None:
        """Clear cached services (useful for testing or hot reloads)."""
        cls._services.clear()

    @classmethod
    def list_loaded_versions(cls) -> List[str]:
        return list(cls._services.keys())
