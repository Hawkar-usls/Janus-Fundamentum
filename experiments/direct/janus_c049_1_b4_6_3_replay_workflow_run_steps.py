#!/usr/bin/env python3
"""Execute every shell `run: |` step from a frozen local GitHub Actions workflow.

The parser intentionally supports only the narrow workflow subset used by the
C049.1 proof chain: named steps, optional scalar environment entries, and
literal shell blocks.  `uses:` steps are not interpreted.  The caller must
perform checkout/runtime setup before invoking this driver.
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Iterable


class WorkflowParseError(RuntimeError):
    pass


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_run_steps(path: Path) -> list[tuple[str, dict[str, str], str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    steps: list[tuple[str, dict[str, str], str]] = []
    current_name = "unnamed"
    current_env: dict[str, str] = {}
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if line.startswith("      - name:"):
            current_name = _scalar(line.split(":", 1)[1])
            current_env = {}
            index += 1
            continue

        if line == "        env:":
            env: dict[str, str] = {}
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip():
                    index += 1
                    continue
                if _indent(candidate) != 10 or ":" not in candidate.strip():
                    break
                key, raw_value = candidate.strip().split(":", 1)
                if not key or not key.replace("_", "").isalnum():
                    raise WorkflowParseError(f"unsupported environment key: {key!r}")
                env[key] = _scalar(raw_value)
                index += 1
            current_env = env
            continue

        if line == "        run: |":
            index += 1
            block: list[str] = []
            while index < len(lines):
                candidate = lines[index]
                if candidate.strip() and _indent(candidate) < 10:
                    break
                if candidate.strip():
                    if _indent(candidate) < 10:
                        raise WorkflowParseError("run block indentation drift")
                    block.append(candidate[10:])
                else:
                    block.append("")
                index += 1
            script = "\n".join(block).rstrip() + "\n"
            if not script.strip():
                raise WorkflowParseError(f"empty run block in step {current_name!r}")
            steps.append((current_name, dict(current_env), script))
            current_env = {}
            continue

        index += 1

    if not steps:
        raise WorkflowParseError("no literal run steps found")
    return steps


def execute_steps(steps: Iterable[tuple[str, dict[str, str], str]]) -> None:
    for ordinal, (name, additions, script) in enumerate(steps, start=1):
        print(f"REPLAY_STEP {ordinal}: {name}", flush=True)
        env = os.environ.copy()
        env.update(additions)
        subprocess.run(
            ["bash", "-euo", "pipefail", "-c", script],
            check=True,
            env=env,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    if not args.workflow.is_file():
        raise SystemExit(f"workflow not found: {args.workflow}")
    steps = parse_run_steps(args.workflow)
    print(f"RUN_STEPS_DISCOVERED = {len(steps)}", flush=True)
    execute_steps(steps)
    print("FROZEN_WORKFLOW_RUN_STEP_REPLAY = PASS", flush=True)


if __name__ == "__main__":
    main()
