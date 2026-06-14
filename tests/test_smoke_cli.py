"""Basic smoke test for Company CLI (no external APIs).
Run with pytest. Tests assume sqlite is writable in repo root.
"""
import subprocess
import sys
import os

PY = sys.executable


def test_init_and_run(tmp_path):
    # Run init to create example team
    p = subprocess.run([PY, "-m", "company.cli", "init", "--team", "smoke-team"], cwd=os.path.dirname(__file__) + "\..", capture_output=True, text=True)
    assert p.returncode == 0
    # Initialize DB
    p = subprocess.run([PY, "-m", "company.cli", "initdb"], cwd=os.path.dirname(__file__) + "\..", capture_output=True, text=True)
    assert p.returncode == 0
    # Run demo
    p = subprocess.run([PY, "-m", "company.cli", "run", "--task", "Smoke test task"], cwd=os.path.dirname(__file__) + "\..", capture_output=True, text=True)
    assert p.returncode == 0
    assert "created" in p.stdout or "Run" in p.stdout
