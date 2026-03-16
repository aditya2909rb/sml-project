from __future__ import annotations

import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _run(command: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, check=False)
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, output.strip()


def _as_repo_relative(path_str: str, repo_root: Path, fallback_name: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        return p
    try:
        return p.relative_to(repo_root)
    except ValueError:
        return Path(fallback_name)


def _copy_path(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        return
    shutil.copy2(src, dest)


def persist_learning_state(repo_root: Path, db_path: str, model_dir: str, branch: str) -> tuple[bool, str]:
    db_src = (repo_root / db_path).resolve() if not Path(db_path).is_absolute() else Path(db_path)
    model_src = (repo_root / model_dir).resolve() if not Path(model_dir).is_absolute() else Path(model_dir)

    if not db_src.exists() and not model_src.exists():
        return False, "no learning artifacts found to persist"

    db_target_rel = _as_repo_relative(str(db_src), repo_root, "sml_state.sqlite3")
    model_target_rel = _as_repo_relative(str(model_src), repo_root, "model_store")

    rc, _ = _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
    if rc != 0:
        return False, "not a git repository"

    with tempfile.TemporaryDirectory(prefix="sml-state-") as tmp:
        worktree = Path(tmp)

        rc_local, _ = _run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=repo_root)
        if rc_local == 0:
            rc_add, out_add = _run(["git", "worktree", "add", "--force", str(worktree), branch], cwd=repo_root)
            if rc_add != 0:
                return False, f"cannot create worktree for local branch {branch}: {out_add}"
        else:
            rc_remote, _ = _run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch], cwd=repo_root)
            if rc_remote == 0:
                _run(["git", "fetch", "origin", f"{branch}:{branch}"], cwd=repo_root)
                rc_add, out_add = _run(["git", "worktree", "add", "--force", str(worktree), branch], cwd=repo_root)
                if rc_add != 0:
                    return False, f"cannot create worktree for fetched branch {branch}: {out_add}"
            else:
                rc_add, out_add = _run(["git", "worktree", "add", "-b", branch, str(worktree), "HEAD"], cwd=repo_root)
                if rc_add != 0:
                    return False, f"cannot create new branch {branch}: {out_add}"

        try:
            if db_src.exists():
                _copy_path(db_src, worktree / db_target_rel)
            if model_src.exists():
                _copy_path(model_src, worktree / model_target_rel)

            _run(["git", "config", "user.email", "sml-bot@users.noreply.github.com"], cwd=worktree)
            _run(["git", "config", "user.name", "sml-bot"], cwd=worktree)

            add_cmd = ["git", "add", "-f"]
            if db_src.exists():
                add_cmd.append(str(db_target_rel))
            if model_src.exists():
                add_cmd.append(str(model_target_rel))
            rc_add_state, out_add_state = _run(add_cmd, cwd=worktree)
            if rc_add_state != 0:
                return False, f"git add failed: {out_add_state}"

            rc_diff, _ = _run(["git", "diff", "--cached", "--quiet"], cwd=worktree)
            if rc_diff == 0:
                return True, "no state changes to commit"

            timestamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
            rc_commit, out_commit = _run(["git", "commit", "-m", f"chore(sml): persist state {timestamp}"], cwd=worktree)
            if rc_commit != 0:
                return False, f"git commit failed: {out_commit}"

            rc_push, out_push = _run(["git", "push", "-u", "origin", branch], cwd=worktree)
            if rc_push != 0:
                return False, f"git push failed: {out_push}"

            return True, f"state committed and pushed to {branch}"
        finally:
            _run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repo_root)
