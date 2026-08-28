"""
Pipeline sub-package for AoE2 Coach replay ingestion, state simulation, and dataset export.
"""

from aoe2_coach.pipeline.parser import (
    ReplayParser,
    ParsedReplayData,
    GameEvent,
    TrainEvent,
    ResearchEvent,
    BuildEvent,
    MoveEvent,
    InteractEvent,
    ChatEvent,
    ResignEvent,
)
from aoe2_coach.pipeline.simulator import (
    GameStateSimulator,
    PlayerStateTracker,
)
from aoe2_coach.pipeline.fog_of_war import (
    FogOfWarEngine,
    PlayerFogOfWarTracker,
)
from aoe2_coach.pipeline.snapshot_extractor import (
    SnapshotExtractor,
)
from aoe2_coach.pipeline.dataset_exporter import (
    DatasetExporter,
    PipelineStats,
)
from aoe2_coach.pipeline.harvester import (
    ReplayHarvester,
    MetadataStore,
    HarvestedMatch,
)

__all__ = [
    "ReplayParser",
    "ParsedReplayData",
    "GameEvent",
    "TrainEvent",
    "ResearchEvent",
    "BuildEvent",
    "MoveEvent",
    "InteractEvent",
    "ChatEvent",
    "ResignEvent",
    "GameStateSimulator",
    "PlayerStateTracker",
    "FogOfWarEngine",
    "PlayerFogOfWarTracker",
    "SnapshotExtractor",
    "DatasetExporter",
    "PipelineStats",
    "ReplayHarvester",
    "MetadataStore",
    "HarvestedMatch",
]
