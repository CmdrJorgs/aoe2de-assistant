"""
Launch script for AoE2 Coach FastAPI Gateway.
"""

import uvicorn
import argparse


def main():
    parser = argparse.ArgumentParser(description="Start AoE2 Coach FastAPI Backend Gateway")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload")
    args = parser.parse_args()

    print(f"Starting AoE2 Coach API Server on http://{args.host}:{args.port}")
    uvicorn.run(
        "aoe2_coach.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
