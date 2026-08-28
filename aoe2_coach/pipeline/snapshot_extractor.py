"""
Snapshot Extractor: Generates time-sliced state-action-outcome training snapshots from parsed replays.
"""

from typing import List, Dict, Optional, Tuple, Any
from collections import Counter

from aoe2_coach.schemas.match import (
    GameSnapshot,
    PlayerState,
    OpponentObservedState,
    TargetLabels,
)
from aoe2_coach.pipeline.parser import (
    ParsedReplayData,
    TrainEvent,
    ResearchEvent,
    BuildEvent,
)
from aoe2_coach.pipeline.simulator import GameStateSimulator
from aoe2_coach.pipeline.fog_of_war import FogOfWarEngine


class SnapshotExtractor:
    """Extracts timestamped training vectors from parsed matches at regular time slices."""

    def __init__(
        self,
        interval_sec: int = 120,
        start_time_sec: int = 360,
        max_time_sec: int = 2700,
        forward_window_sec: int = 300,
    ):
        self.interval_sec = interval_sec
        self.start_time_sec = start_time_sec
        self.max_time_sec = max_time_sec
        self.forward_window_sec = forward_window_sec

    def extract_snapshots(self, parsed_data: ParsedReplayData) -> List[GameSnapshot]:
        """Extract all time-series snapshots for both players across the match duration."""
        metadata = parsed_data.metadata
        duration_sec = metadata.duration_sec
        events = parsed_data.events

        if duration_sec < self.start_time_sec:
            # Game is too short for meaningful mid-game snapshots
            return []

        simulator = GameStateSimulator(parsed_data)
        fow_engine = FogOfWarEngine(parsed_data)

        snapshots: List[GameSnapshot] = []

        end_time = int(min(duration_sec, self.max_time_sec))

        for t in range(self.start_time_sec, end_time, self.interval_sec):
            player_states = simulator.step_to_time(float(t))
            observed_states = fow_engine.step_to_time(float(t))

            # Extract snapshot for each player perspective
            for pid, player_state in player_states.items():
                if pid not in observed_states:
                    continue

                observed_state = observed_states[pid]
                target_labels = self._compute_target_labels(
                    events=events,
                    player_id=pid,
                    current_time_sec=float(t),
                    forward_window_sec=self.forward_window_sec,
                    is_winner=player_state.elo is not None and metadata.winning_player_id == pid,
                )

                snapshot = GameSnapshot(
                    match_id=metadata.match_id,
                    patch_version=metadata.patch_version,
                    timestamp_sec=t,
                    map_type=metadata.map_name,
                    player=player_state,
                    opponent_observed=observed_state,
                    label=target_labels,
                )
                snapshots.append(snapshot)

        return snapshots

    def _compute_target_labels(
        self,
        events: List[Any],
        player_id: int,
        current_time_sec: float,
        forward_window_sec: float,
        is_winner: bool,
    ) -> TargetLabels:
        """Analyze player actions in the subsequent [t, t + forward_window] time window."""
        window_end = current_time_sec + forward_window_sec

        next_unit: Optional[str] = None
        next_tech: Optional[str] = None
        next_building: Optional[str] = None
        unit_counts_next = Counter()
        action_vector = Counter()

        for ev in events:
            if ev.player_id != player_id:
                continue
            if ev.timestamp_sec <= current_time_sec:
                continue
            if ev.timestamp_sec > window_end:
                break

            if isinstance(ev, TrainEvent):
                action_vector[f"train_{ev.canonical_name}"] += ev.amount
                if ev.canonical_name != "villager":
                    unit_counts_next[ev.canonical_name] += ev.amount
                    if next_unit is None:
                        next_unit = ev.canonical_name

            elif isinstance(ev, ResearchEvent):
                action_vector[f"tech_{ev.canonical_name}"] += 1
                if next_tech is None:
                    next_tech = ev.canonical_name

            elif isinstance(ev, BuildEvent):
                action_vector[f"build_{ev.canonical_name}"] += 1
                if next_building is None and ev.canonical_name not in {"house", "farm"}:
                    next_building = ev.canonical_name

        primary_comp = unit_counts_next.most_common(1)[0][0] if unit_counts_next else None

        return TargetLabels(
            winner=is_winner,
            next_unit_produced=next_unit,
            next_tech_researched=next_tech,
            next_building_built=next_building,
            primary_composition_next_5m=primary_comp,
            action_vector_next_5m=dict(action_vector),
        )
