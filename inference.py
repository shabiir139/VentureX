#!/usr/bin/env python3
"""
Inference Script — VentureX Business Simulation
"""

import asyncio
import os
import sys
import json
import textwrap
from typing import List, Optional

from openai import OpenAI
from venturex_env import VentureXEnvClient, VentureXAction, VentureXObservation

# CONFIG
IMAGE_NAME = os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api-inference.huggingface.co/models"
MODEL_NAME = os.getenv("MODEL_NAME") or "mistralai/Mistral-7B-Instruct-v0.2"
BENCHMARK = os.getenv("VENTUREX_BENCHMARK", "venturex")
MAX_STEPS = 90
TEMPERATURE = 0.7
MAX_TOKENS = 300

TASK_NAMES = ["grow_startup", "survive_downturn", "reach_profitability", "market_expansion"]
SUCCESS_SCORE_THRESHOLD = 0.3

SYSTEM_PROMPT = textwrap.dedent("""
You are VentureX AI — an expert startup CEO agent playing a business simulation.
Respond with ONLY a valid JSON object.
""").strip()

# LOGGING
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(task: str, success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] task={task} success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

# PROMPT
def build_user_prompt(step, task_description, obs, last_reward, history):
    return f"Step {step}, Cash: {obs.cash}, Revenue: {obs.revenue}"

# LLM
def get_model_action(client, step, task_description, obs, last_reward, history):
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(step, task_description, obs, last_reward, history)},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        content = completion.choices[0].message.content.strip()
        data = json.loads(content)

        return VentureXAction(
            action_type=data.get("action_type", "allocate_budget"),
            department=data.get("department", "executive"),
            parameters=data.get("parameters", {}),
            reasoning=data.get("reasoning", ""),
        )
    except:
        return VentureXAction(
            action_type="allocate_budget",
            department="marketing",
            parameters={"amount": 50000},
            reasoning="fallback",
        )

# RUN TASK
async def run_task(task_name, task_description, max_steps):
    from tasks import ALL_TASKS
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    if IMAGE_NAME:
        env = await VentureXEnvClient.from_docker_image(IMAGE_NAME, task_name=task_name)
    else:
        env = await VentureXEnvClient.from_local(task_name=task_name)

    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task_name, BENCHMARK, MODEL_NAME)

    try:
        result = await env.reset()
        obs = result.observation
        last_reward = 0.0
        history = []

        for step in range(1, max_steps + 1):
            if result.done:
                break

            action = get_model_action(client, step, task_description, obs, last_reward, history)
            result = await env.step(action)

            reward = result.reward
            done = result.done
            error = result.last_action_error

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step, str(action), reward, done, error)

            if done:
                break

        final_scores = await env.get_score()
        score = sum(rewards) / max(len(rewards), 1)
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)

        log_end(task_name, success, steps_taken, score, rewards)

    return score

# MAIN
async def main():
    from tasks import ALL_TASKS

    for task_name in TASK_NAMES:
        task_config = ALL_TASKS.get(task_name)
        if not task_config:
            continue

        await run_task(task_name, task_config.description, task_config.max_days)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Top level unhandled exception: {e}", flush=True)
        sys.exit(1)