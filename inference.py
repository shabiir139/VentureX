#!/usr/bin/env python3
"""
Inference Script — VentureX Business Simulation
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    LOCAL_IMAGE_NAME The name of the local image to use for the environment if you are using from_docker_image()

- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT
- The script emits exactly three line types to stdout:
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import asyncio
import os
import sys
import json
import textwrap
from typing import List, Optional

from openai import OpenAI

from venturex_env import VentureXEnvClient, VentureXAction, VentureXObservation

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
IMAGE_NAME = os.getenv("IMAGE_NAME")  # If using docker image
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api-inference.huggingface.co/models"
MODEL_NAME = os.getenv("MODEL_NAME") or "mistralai/Mistral-7B-Instruct-v0.2"
BENCHMARK = os.getenv("VENTUREX_BENCHMARK", "venturex")
MAX_STEPS = 90
TEMPERATURE = 0.7
MAX_TOKENS = 300

# Tasks to run
TASK_NAMES = ["grow_startup", "survive_downturn", "reach_profitability", "market_expansion"]

# Score thresholds
SUCCESS_SCORE_THRESHOLD = 0.3  # normalized score in [0, 1]

# ═══════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = textwrap.dedent("""
You are VentureX AI — an expert startup CEO agent playing a business simulation.
Each turn you receive the current state of your company and must choose ONE action.

Available actions (pick exactly one):
- allocate_budget: Set budget for a department. Params: {"amount": <number>}
- hire: Hire employees. Params: {"count": <number 1-10>}
- set_price: Set product price. Params: {"amount": <number>}
- launch_product: Launch a product. Params: {"cost": <number>}
- raise_funding: Attempt to raise venture funding. Params: {}
- pivot: Pivot strategy. Params: {}
- expand_market: Expand into new markets. Params: {"cost": <number>}
- cut_costs: Cut costs across departments. Params: {"percentage": <number 5-50>}
- invest_rd: Invest in R&D. Params: {"amount": <number>}
- run_marketing_campaign: Run a marketing campaign. Params: {"budget": <number>}

Departments: marketing, finance, operations, hr, product, executive

Respond with ONLY a valid JSON object:
{"action_type": "...", "department": "...", "parameters": {...}, "reasoning": "..."}

Think strategically about:
1. Current stage and advancement criteria
2. Cash position and burn rate
3. Market conditions and competition
4. Active events/disruptions
5. Long-term sustainability vs short-term gains
""").strip()


# ═══════════════════════════════════════════════════════════════════════════
#  STRUCTURED STDOUT LOGGING (EXACT FORMAT)
# ═══════════════════════════════════════════════════════════════════════════
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  LLM DECISION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════
def build_user_prompt(
    step: int,
    task_description: str,
    obs: VentureXObservation,
    last_reward: float,
    history: List[str],
) -> str:
    history_block = "\n".join(history[-5:]) if history else "None"
    events_block = ", ".join(obs.active_events) if obs.active_events else "None"
    return textwrap.dedent(f"""
TASK: {task_description}

CURRENT STATE (Day {obs.day}):
  Stage: {obs.stage}
  Cash: ${obs.cash:,.0f}
  Revenue: ${obs.revenue:,.0f}
  Market Share: {obs.market_share:.1%}
  Customer Satisfaction: {obs.satisfaction:.0%}
  Burn Rate: ${obs.burn_rate:,.0f}/day
  Employees: {obs.employee_count}
  Active Events: {events_block}

Last Reward: {last_reward:.2f}

Recent History:
{history_block}

Choose your action for Day {obs.day}. Respond with ONLY valid JSON.
    """).strip()


def get_model_action(
    client: OpenAI,
    step: int,
    task_description: str,
    obs: VentureXObservation,
    last_reward: float,
    history: List[str],
) -> VentureXAction:
    """Query the LLM for a business decision."""
    user_prompt = build_user_prompt(step, task_description, obs, last_reward, history)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = (completion.choices[0].message.content or "").strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Find JSON object in content
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            content = content[start_idx:end_idx]

        data = json.loads(content)
        return VentureXAction(
            action_type=data.get("action_type", "allocate_budget"),
            department=data.get("department", "executive"),
            parameters=data.get("parameters", {}),
            reasoning=data.get("reasoning", ""),
        )
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        # Fallback action
        return VentureXAction(
            action_type="allocate_budget",
            department="marketing",
            parameters={"amount": 60000},
            reasoning=f"Fallback due to: {str(exc)[:50]}",
        )


# ═══════════════════════════════════════════════════════════════════════════
#  RUN A SINGLE TASK
# ═══════════════════════════════════════════════════════════════════════════
async def run_task(task_name: str, task_description: str, max_steps: int) -> float:
    """Run a single graded task. Returns score in [0, 1]."""
    from tasks import ALL_TASKS
    from graders.grader_startup import GrowStartupGrader
    from graders.grader_downturn import SurviveDownturnGrader
    from graders.grader_profit import ProfitabilityGrader
    from graders.grader_expansion import MarketExpansionGrader

    grader_map = {
        "grow_startup": GrowStartupGrader(),
        "survive_downturn": SurviveDownturnGrader(),
        "reach_profitability": ProfitabilityGrader(),
        "market_expansion": MarketExpansionGrader(),
    }

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Create environment (Docker or local)
    if IMAGE_NAME:
        env = await VentureXEnvClient.from_docker_image(IMAGE_NAME, task_name=task_name)
    else:
        env = await VentureXEnvClient.from_local(task_name=task_name)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset()
        obs = result.observation
        last_reward = 0.0

        for step in range(1, max_steps + 1):
            if result.done:
                break

            # Get LLM decision
            action = get_model_action(client, step, task_description, obs, last_reward, history)

            # Execute step
            result = await env.step(action)
            obs = result.observation

            reward = result.reward
            done = result.done
            error = result.last_action_error

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            # Log step in exact format
            log_step(
                step=step,
                action=str(action),
                reward=reward,
                done=done,
                error=error,
            )

            history.append(
                f"Day {obs.day}: {action.action_type}({action.department}) -> reward={reward:.2f}"
            )

            if done:
                break

        # Grade the run
        final_scores = await env.get_score()
        grader = grader_map.get(task_name)
        if grader:
            grade_result = grader.grade(final_scores)
            score = grade_result["score"]
        else:
            score = sum(rewards) / max(len(rewards), 1)

        score = min(max(score, 0.0), 1.0)  # clamp to [0, 1]
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)

        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
async def main() -> None:
    """Run all tasks and report results."""
    from tasks import ALL_TASKS

    all_scores = {}

    for task_name in TASK_NAMES:
        task_config = ALL_TASKS.get(task_name)
        if not task_config:
            print(f"[DEBUG] Task {task_name} not found, skipping", flush=True)
            continue

        score = await run_task(
            task_name=task_name,
            task_description=task_config.description,
            max_steps=task_config.max_days,
        )
        all_scores[task_name] = score

    # Summary (not part of required format, but helpful for debugging)
    if all_scores:
        avg = sum(all_scores.values()) / len(all_scores)
        print(f"\n[SUMMARY] average_score={avg:.2f} tasks={len(all_scores)}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
