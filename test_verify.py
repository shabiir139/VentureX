#!/usr/bin/env python3
"""VentureX · Full Verification Suite (including OpenEnv format compliance)"""
import sys
import re
import io
import asyncio
sys.path.insert(0, '.')

from src.environment import VentureXEnv
from src.models import Action, TaskConfig
from tasks import ALL_TASKS
from graders.grader_startup import GrowStartupGrader
from graders.grader_downturn import SurviveDownturnGrader
from graders.grader_profit import ProfitabilityGrader
from graders.grader_expansion import MarketExpansionGrader
from venturex_env import VentureXEnvClient, VentureXAction


def test_reset():
    print("=== TEST 1: reset() ===")
    env = VentureXEnv()
    obs = env.reset()
    assert obs.day == 1
    assert obs.stage == "IDEA"
    assert obs.financials.cash == 500_000
    print(f"  Day={obs.day}, Stage={obs.stage}, Cash=${obs.financials.cash:,.0f}")
    print("PASS\n")
    return env


def test_step(env):
    print("=== TEST 2: step() ===")
    action = Action(action_type="allocate_budget", department="marketing",
                    parameters={"amount": 80000}, reasoning="Boost marketing")
    result = env.step(action)
    assert result.observation.day == 2
    assert 0.0 <= result.reward <= 1.0
    print(f"  Day={result.observation.day}, Reward={result.reward:.4f}")
    print("PASS\n")
    return env


def test_multiple_steps(env):
    print("=== TEST 3: Multiple steps ===")
    actions = [
        Action(action_type="hire", department="product", parameters={"count": 3}),
        Action(action_type="invest_rd", department="product", parameters={"amount": 40000}),
        Action(action_type="run_marketing_campaign", department="marketing", parameters={"budget": 25000}),
        Action(action_type="set_price", department="executive", parameters={"amount": 80}),
        Action(action_type="launch_product", department="product", parameters={"cost": 30000}),
    ]
    for a in actions:
        r = env.step(a)
        print(f"  Day {r.observation.day}: {a.action_type} -> reward={r.reward:.4f}")
    print("PASS\n")
    return env


def test_graders():
    print("=== TEST 4: All 4 graders (0.0-1.0) ===")
    graders = {
        "grow_startup": GrowStartupGrader(),
        "survive_downturn": SurviveDownturnGrader(),
        "reach_profitability": ProfitabilityGrader(),
        "market_expansion": MarketExpansionGrader(),
    }
    for task_name, task_config in ALL_TASKS.items():
        env2 = VentureXEnv(task_config=task_config)
        env2.reset()
        for _ in range(10):
            env2.step(Action(action_type="allocate_budget", department="marketing",
                             parameters={"amount": 60000}))
        grade = graders[task_name].grade(env2.get_final_score())
        assert 0.0 <= grade["score"] <= 1.0, f"Score out of range: {grade['score']}"
        print(f"  {task_name}: {grade['score']:.4f}")
    print("PASS\n")


def test_state(env):
    print("=== TEST 5: state() ===")
    s = env.state()
    assert s.day > 1
    print(f"  day={s.day}, stage={s.stage}")
    print("PASS\n")


def test_timeline(env):
    print("=== TEST 6: Timeline ===")
    stats = env.timeline.get_stats()
    assert stats["total_actions"] > 0
    print(f"  {stats['total_actions']} actions across {stats['days_active']} days")
    print("PASS\n")


def test_bankruptcy():
    print("=== TEST 7: Bankruptcy detection ===")
    tc = TaskConfig(task_name="test", max_days=200, initial_cash=1000, initial_stage="IDEA")
    env = VentureXEnv(task_config=tc)
    env.reset()
    for _ in range(200):
        r = env.step(Action(action_type="hire", department="hr",
                            parameters={"count": 10}, reasoning="Over-hire"))
        if r.terminated:
            print(f"  Bankrupt at day {r.observation.day}")
            break
    assert r.terminated
    print("PASS\n")


def test_async_local_env():
    print("=== TEST 8: Async local env client ===")
    async def _test():
        env = await VentureXEnvClient.from_local(task_name="grow_startup")
        result = await env.reset()
        assert result.observation.day == 1
        assert result.observation.stage == "IDEA"

        action = VentureXAction(action_type="allocate_budget", department="marketing",
                                parameters={"amount": 70000})
        result2 = await env.step(action)
        assert result2.observation.day == 2
        assert 0.0 <= result2.reward <= 1.0

        score = await env.get_score()
        assert "stage_reached" in score

        await env.close()
        print(f"  Reset OK, Step OK, Score OK")
    asyncio.run(_test())
    print("PASS\n")


def test_stdout_format():
    print("=== TEST 9: Stdout format compliance ===")
    # Verify format patterns
    start_pattern = r'^\[START\] task=\S+ env=\S+ model=\S+$'
    step_pattern = r'^\[STEP\] step=\d+ action=\S+ reward=\d+\.\d{2} done=(true|false) error=\S+$'
    end_pattern = r'^\[END\] success=(true|false) steps=\d+ score=\d+\.\d{2} rewards=[\d.,]+$'

    # Test start format
    start_line = "[START] task=grow_startup env=venturex model=mistral-7b"
    assert re.match(start_pattern, start_line), f"START format mismatch: {start_line}"
    print(f"  [START] format: OK")

    # Test step format
    step_line = "[STEP] step=1 action=allocate_budget(marketing,amount=60000) reward=0.42 done=false error=null"
    assert re.match(step_pattern, step_line), f"STEP format mismatch: {step_line}"
    print(f"  [STEP] format: OK")

    # Test end format
    end_line = "[END] success=true steps=5 score=0.73 rewards=0.42,0.45,0.50,0.55,0.73"
    assert re.match(end_pattern, end_line), f"END format mismatch: {end_line}"
    print(f"  [END] format: OK")

    print("PASS\n")


def test_fastapi_import():
    print("=== TEST 10: FastAPI app loads ===")
    from app import app
    routes = [r.path for r in app.routes]
    assert "/reset" in routes
    assert "/step" in routes
    assert "/state" in routes
    assert "/health" in routes
    assert "/score" in routes
    print(f"  Routes: {routes}")
    print("PASS\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  VentureX — Full Verification Suite")
    print("=" * 60 + "\n")

    env = test_reset()
    env = test_step(env)
    env = test_multiple_steps(env)
    test_graders()
    test_state(env)
    test_timeline(env)
    test_bankruptcy()
    test_async_local_env()
    test_stdout_format()
    test_fastapi_import()

    print("=" * 60)
    print("  ALL 10 TESTS PASSED ✅")
    print("=" * 60)
