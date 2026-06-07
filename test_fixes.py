from src.utils.config import clean_and_parse_json

print("=== Testing clean_and_parse_json fixes ===\n")

# Test 1: Invalid escape sequences (like \w, \p etc. from model)
t1 = '{"key": "hello \\world and \\path", "val": 1}'
try:
    r = clean_and_parse_json(t1)
    print(f"OK  T1 invalid escape fixed -> {r}")
except Exception as e:
    print(f"FAIL T1: {e}")

# Test 2: Truncated JSON (model hit token limit)
t2 = '{"tasks": [{"id": 1, "name": "search"'
try:
    r = clean_and_parse_json(t2)
    print(f"OK  T2 truncated JSON repaired -> {r}")
except Exception as e:
    print(f"FAIL T2: {e}")

# Test 3: Think block + markdown fences
t3 = '<think>some reasoning...</think>\n```json\n{"plan_id": "plan_001", "score": 0.95}\n```'
try:
    r = clean_and_parse_json(t3)
    print(f"OK  T3 think+fence stripped -> {r}")
except Exception as e:
    print(f"FAIL T3: {e}")

# Test 4: Trailing comma
t4 = '{"a": 1, "b": 2,}'
try:
    r = clean_and_parse_json(t4)
    print(f"OK  T4 trailing comma removed -> {r}")
except Exception as e:
    print(f"FAIL T4: {e}")

# Test 5: Float durations in planner
from src.agents.planner import SubTask, TaskType, TaskPriority
try:
    t = SubTask(
        task_id="task_001",
        task_type=TaskType.WEB_SEARCH,
        description="Search for EV risks",
        priority=TaskPriority.HIGH,
        agent="Researcher",
        estimated_duration_seconds=1.5  # float from model
    )
    print(f"OK  T5 SubTask accepts float duration -> {t.estimated_duration_seconds}")
except Exception as e:
    print(f"FAIL T5: {e}")

print("\nAll tests done.")
