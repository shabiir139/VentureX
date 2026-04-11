# ─── VentureX · FastAPI Server ──────────────────────────────────────────────
"""
OpenEnv-compliant API server with /reset, /step, /state endpoints.
Deployed on HuggingFace Spaces at port 7860.
"""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.models import Action, Observation, StepResult, TaskConfig
from src.environment import VentureXEnv
from tasks import ALL_TASKS

# ═══════════════════════════════════════════════════════════════════════════
#  APP SETUP
# ═══════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="VentureX",
    description=(
        "AI-powered business simulation environment. "
        "Test startup ideas in a day-by-day simulated economy with real-world scenarios."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global environment instance ──
_env: VentureXEnv | None = None


def _get_env() -> VentureXEnv:
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    return _env


# ═══════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check — must return 200 for HF Spaces ping."""
    return {"status": "ok", "service": "venturex", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint — returns API info."""
    return {
        "name": "VentureX",
        "description": "Business Simulation Environment",
        "endpoints": ["/reset", "/step", "/state", "/health", "/tasks"],
        "version": "1.0.0",
    }


@app.get("/tasks")
async def list_tasks():
    """List all available tasks with descriptions."""
    return {
        "tasks": [
            {
                "name": t.task_name,
                "description": t.description,
                "max_days": t.max_days,
                "initial_stage": t.initial_stage,
                "initial_cash": t.initial_cash,
            }
            for t in ALL_TASKS.values()
        ]
    }


from pydantic import BaseModel

class ResetRequest(BaseModel):
    task_name: str | None = None

@app.post("/reset", response_model=Observation)
async def reset(request: ResetRequest | None = None):
    """
    Initialize a new simulation episode.
    Optionally specify a task_name to configure for a specific graded task.
    """
    global _env

    task_config = None
    if request and request.task_name:
        if request.task_name not in ALL_TASKS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task: {request.task_name}. Available: {list(ALL_TASKS.keys())}",
            )
        task_config = ALL_TASKS[request.task_name]

    _env = VentureXEnv(task_config=task_config)
    observation = _env.reset()
    return observation


@app.post("/step", response_model=StepResult)
async def step(action: Action):
    """
    Execute a business decision and advance one simulated day.
    Returns the new observation, reward (0.0-1.0), and termination signals.
    """
    env = _get_env()
    result = env.step(action)
    return result


@app.get("/state", response_model=Observation)
async def state():
    """Get current simulation state without advancing time."""
    env = _get_env()
    return env.state()


@app.get("/score")
async def get_score():
    """Get the final scoring breakdown for the current episode."""
    env = _get_env()
    return env.get_final_score()


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════
def main():
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
