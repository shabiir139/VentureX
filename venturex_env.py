# ─── VentureX · OpenEnv Client ──────────────────────────────────────────────
"""
OpenEnv-compatible environment client for VentureX.
Supports both local (in-process) and Docker-based (HTTP) execution.
"""
from __future__ import annotations

import asyncio
import subprocess
import time
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from src.models import Action, Observation, StepResult, TaskConfig
from src.environment import VentureXEnv
from tasks import ALL_TASKS


# ═══════════════════════════════════════════════════════════════════════════
#  RESULT WRAPPERS (match OpenEnv interface)
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class VentureXObservation:
    """Observation wrapper matching OpenEnv pattern."""
    day: int = 1
    stage: str = "IDEA"
    cash: float = 500_000
    revenue: float = 0
    market_share: float = 0.05
    satisfaction: float = 0.7
    burn_rate: float = 0
    employee_count: int = 5
    status_summary: str = ""
    available_actions: list[str] = field(default_factory=list)
    active_events: list[str] = field(default_factory=list)

    @classmethod
    def from_observation(cls, obs: Observation) -> "VentureXObservation":
        return cls(
            day=obs.day,
            stage=obs.stage,
            cash=obs.financials.cash,
            revenue=obs.financials.revenue,
            market_share=obs.market.market_share,
            satisfaction=obs.market.customer_satisfaction,
            burn_rate=obs.financials.burn_rate,
            employee_count=obs.employee_count,
            status_summary=obs.status_summary,
            available_actions=obs.available_actions,
            active_events=[e.name for e in obs.active_events],
        )

    @classmethod
    def from_dict(cls, d: dict) -> "VentureXObservation":
        fin = d.get("financials", {})
        mkt = d.get("market", {})
        return cls(
            day=d.get("day", 1),
            stage=d.get("stage", "IDEA"),
            cash=fin.get("cash", 0),
            revenue=fin.get("revenue", 0),
            market_share=mkt.get("market_share", 0.05),
            satisfaction=mkt.get("customer_satisfaction", 0.7),
            burn_rate=fin.get("burn_rate", 0),
            employee_count=d.get("employee_count", 5),
            status_summary=d.get("status_summary", ""),
            available_actions=d.get("available_actions", []),
            active_events=[e.get("name", "") for e in d.get("active_events", [])],
        )


@dataclass
class VentureXResult:
    """Step result wrapper matching OpenEnv pattern."""
    observation: VentureXObservation
    reward: float = 0.0
    done: bool = False
    info: dict = field(default_factory=dict)
    last_action_error: Optional[str] = None


@dataclass
class VentureXAction:
    """Action wrapper matching OpenEnv pattern."""
    action_type: str = "allocate_budget"
    department: str = "executive"
    parameters: dict = field(default_factory=dict)
    reasoning: str = ""

    def to_action(self) -> Action:
        return Action(
            action_type=self.action_type,
            department=self.department,
            parameters=self.parameters,
            reasoning=self.reasoning,
        )

    def to_dict(self) -> dict:
        return {
            "action_type": self.action_type,
            "department": self.department,
            "parameters": self.parameters,
            "reasoning": self.reasoning,
        }

    def __str__(self) -> str:
        params = ",".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.action_type}({self.department},{params})"


# ═══════════════════════════════════════════════════════════════════════════
#  VENTUREX ENV CLIENT
# ═══════════════════════════════════════════════════════════════════════════
class VentureXEnvClient:
    """
    OpenEnv-compatible client for VentureX simulation.
    Can run locally (in-process) or connect to a Docker container.
    """

    def __init__(self, mode: str = "local", base_url: str = "", task_name: str = "grow_startup"):
        self.mode = mode
        self.base_url = base_url.rstrip("/")
        self.task_name = task_name
        self._env: Optional[VentureXEnv] = None
        self._container_id: Optional[str] = None
        self._http: Optional[httpx.AsyncClient] = None

    @classmethod
    async def from_docker_image(cls, image_name: str, task_name: str = "grow_startup") -> "VentureXEnvClient":
        """Start environment from a Docker image (OpenEnv pattern)."""
        client = cls(mode="docker", task_name=task_name)

        # Start the Docker container
        proc = subprocess.run(
            ["docker", "run", "-d", "-p", "7860:7860", image_name],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Docker run failed: {proc.stderr}")

        client._container_id = proc.stdout.strip()
        client.base_url = "http://localhost:7860"
        client._http = httpx.AsyncClient(base_url=client.base_url, timeout=30.0)

        # Wait for server to be ready
        for _ in range(30):
            try:
                resp = await client._http.get("/health")
                if resp.status_code == 200:
                    break
            except Exception:
                pass
            await asyncio.sleep(1)

        return client

    @classmethod
    async def from_http(cls, base_url: str, task_name: str = "grow_startup") -> "VentureXEnvClient":
        """Connect to an already running environment over HTTP."""
        client = cls(mode="http", base_url=base_url, task_name=task_name)
        client._http = httpx.AsyncClient(base_url=client.base_url, timeout=30.0)
        
        # Wait for server to be ready
        for _ in range(30):
            try:
                resp = await client._http.get("/health")
                if resp.status_code == 200:
                    break
            except Exception:
                pass
            await asyncio.sleep(1)
            
        return client

    @classmethod
    async def from_local(cls, task_name: str = "grow_startup") -> "VentureXEnvClient":
        """Create environment running locally (in-process, no Docker)."""
        client = cls(mode="local", task_name=task_name)
        return client

    async def reset(self) -> VentureXResult:
        """Reset the environment and return initial observation."""
        if self.mode == "local":
            task_config = ALL_TASKS.get(self.task_name)
            self._env = VentureXEnv(task_config=task_config)
            obs = self._env.reset()
            return VentureXResult(
                observation=VentureXObservation.from_observation(obs),
                reward=0.0,
                done=False,
            )
        else:
            try:
                resp = await self._http.post("/reset", json={"task_name": self.task_name})
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[DEBUG] HTTP /reset failed: {e}", file=sys.stderr, flush=True)
                data = {}
                
            return VentureXResult(
                observation=VentureXObservation.from_dict(data),
                reward=0.0,
                done=False,
            )

    async def step(self, action: VentureXAction) -> VentureXResult:
        """Execute an action and advance one day."""
        if self.mode == "local":
            result = self._env.step(action.to_action())
            return VentureXResult(
                observation=VentureXObservation.from_observation(result.observation),
                reward=result.reward,
                done=result.terminated or result.truncated,
                info=result.info,
                last_action_error=result.info.get("termination_reason"),
            )
        else:
            try:
                resp = await self._http.post("/step", json=action.to_dict())
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[DEBUG] HTTP /step failed: {e}", file=sys.stderr, flush=True)
                data = {"observation": {}, "reward": 0.0, "terminated": True}
                
            obs_data = data.get("observation", {})
            terminated = data.get("terminated", False)
            truncated = data.get("truncated", False)
            info = data.get("info", {})
            return VentureXResult(
                observation=VentureXObservation.from_dict(obs_data),
                reward=data.get("reward", 0.0),
                done=terminated or truncated,
                info=info,
                last_action_error=info.get("termination_reason"),
            )

    async def get_score(self) -> dict:
        """Get final scoring breakdown."""
        if self.mode == "local":
            return self._env.get_final_score()
        else:
            resp = await self._http.get("/score")
            resp.raise_for_status()
            return resp.json()

    async def close(self) -> None:
        """Clean up resources."""
        if self._http:
            await self._http.aclose()
        if self._container_id:
            subprocess.run(
                ["docker", "rm", "-f", self._container_id],
                capture_output=True,
            )
