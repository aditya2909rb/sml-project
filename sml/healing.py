from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HealResult:
    checks_ok: bool
    healed: bool
    details: str


def _run(command: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, check=False)
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, output.strip()


def run_checks(repo_root: Path) -> tuple[bool, str]:
    code, output = _run(["python", "-m", "pytest", "-q"], cwd=repo_root)
    return code == 0, output


def attempt_self_heal(repo_root: Path) -> HealResult:
    ok, check_output = run_checks(repo_root)
    if ok:
        return HealResult(checks_ok=True, healed=False, details="checks already passing")

    fix_steps = [
        ["python", "-m", "ruff", "check", "--fix", "."],
        ["python", "-m", "black", "."],
    ]

    logs: list[str] = ["initial checks failed", check_output]
    for cmd in fix_steps:
        code, out = _run(cmd, cwd=repo_root)
        logs.append(f"$ {' '.join(cmd)}")
        logs.append(out)
        if code != 0:
            logs.append("fix command returned non-zero exit code")

    ok_after, final_output = run_checks(repo_root)
    logs.append("checks after healing")
    logs.append(final_output)

    return HealResult(
        checks_ok=ok_after,
        healed=ok_after,
        details="\n\n".join(logs),
    )
