"""
FastAPI Application Factory for AoE2 Coach.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aoe2_coach.api.routes import router
from aoe2_coach.api.service import CoachAPIService

logger = logging.getLogger("aoe2_coach.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: instantiate services and warmup models."""
    logger.info("Initializing AoE2 Coach ML & Rules Services...")
    service = CoachAPIService()
    app.state.coach_service = service
    logger.info("AoE2 Coach Services ready for inference.")
    yield
    logger.info("Shutting down AoE2 Coach Services.")


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""
    app = FastAPI(
        title="AoE2 Coach AI — Real-Time Strategic & Tactical Gateway",
        description="Low-latency inference & tactical decision-support API for Age of Empires II: DE.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware for Next.js frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


app = create_app()
