"""
FastAPI Route Handlers for AoE2 Coach Gateway.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from aoe2_coach.api.schemas import (
    SnapshotInput,
    RecommendationResponse,
    CounterMatrixRequest,
    CounterMatrixResponse,
    EconomySolverRequest,
    EconomySolverResponse,
    VoiceParseRequest,
    VoiceParseResponse,
    CombatSimRequest,
    CombatSimResponse,
    PresetScenario,
    HealthResponse,
)
from aoe2_coach.api.presets import PRESET_SCENARIOS
from aoe2_coach.api.voice_parser import VoiceTranscriptParser
from aoe2_coach.api.service import CoachAPIService

router = APIRouter(prefix="/api")


def get_service(request: Request) -> CoachAPIService:
    """Dependency injector for CoachAPIService."""
    return request.app.state.coach_service


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def get_health(service: CoachAPIService = Depends(get_service)):
    """System health check, ML model status, and LLM readiness."""
    return service.check_health()


@router.post("/tactical/recommend", response_model=RecommendationResponse, tags=["Tactical Decision Support"])
async def get_tactical_recommendation(
    payload: SnapshotInput,
    service: CoachAPIService = Depends(get_service),
):
    """
    Generate unified tactical recommendation:
    Feeds match snapshot through ML ONNX models, AoE2 Rules Engine,
    and verified ELO-calibrated LLM coaching explainer.
    """
    try:
        return service.generate_recommendation(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")


@router.post("/tactical/counter-matrix", response_model=CounterMatrixResponse, tags=["Domain Rules"])
async def query_counter_matrix(
    payload: CounterMatrixRequest,
    service: CoachAPIService = Depends(get_service),
):
    """Real-time counter matrix engine for spotted enemy compositions."""
    try:
        return service.compute_counter_matrix(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Counter matrix error: {str(e)}")


@router.post("/tactical/economy-solver", response_model=EconomySolverResponse, tags=["Macro Economy"])
async def query_economy_solver(
    payload: EconomySolverRequest,
    service: CoachAPIService = Depends(get_service),
):
    """Calculate exact villager allocations to sustain continuous military production."""
    try:
        return service.solve_economy(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Economy solver error: {str(e)}")


@router.post("/tactical/voice-parse", response_model=VoiceParseResponse, tags=["Voice & Natural Language"])
async def parse_voice_transcript(
    payload: VoiceParseRequest,
):
    """
    Parse spoken voice text into structured match snapshot state.
    Allows players to speak natural RTS updates mid-game in under 5 seconds.
    """
    try:
        return VoiceTranscriptParser.parse(
            transcript=payload.transcript,
            current_snapshot=payload.current_snapshot,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice parser error: {str(e)}")


@router.post("/tactical/simulate", response_model=CombatSimResponse, tags=["Combat Simulator"])
async def simulate_combat_engagement(
    payload: CombatSimRequest,
    service: CoachAPIService = Depends(get_service),
):
    """Simulate damage and combat engagement between two unit armies."""
    try:
        return service.simulate_combat(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combat simulator error: {str(e)}")


@router.get("/meta/civs", response_model=List[Dict[str, Any]], tags=["Metadata"])
async def get_civilizations(service: CoachAPIService = Depends(get_service)):
    """List of all 45+ AoE2 civilizations with bonuses and unique units."""
    return service.get_civ_list()


@router.get("/meta/units", response_model=List[Dict[str, Any]], tags=["Metadata"])
async def get_units(service: CoachAPIService = Depends(get_service)):
    """Full unit catalog with costs, stats, and counters."""
    return service.get_unit_catalog()


@router.get("/meta/presets", response_model=List[PresetScenario], tags=["Metadata"])
async def get_preset_scenarios():
    """Curated match presets for 1-click test loading."""
    return PRESET_SCENARIOS


@router.get("/meta/presets/{preset_id}", response_model=PresetScenario, tags=["Metadata"])
async def get_preset_by_id(preset_id: str):
    """Retrieve specific preset scenario by ID."""
    for p in PRESET_SCENARIOS:
        if p.id == preset_id:
            return p
    raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
