from __future__ import annotations

import json
from pathlib import Path
import sys

from task_engine import build_plan


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python main.py INPUT.json", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        plan = build_plan(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
