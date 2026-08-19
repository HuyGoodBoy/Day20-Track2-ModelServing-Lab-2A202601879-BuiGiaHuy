#!/usr/bin/env python3
"""One-shot lab setup: probe -> runtime -> model.

Cross-platform and compiler-free. The virtualenv and pip install happen before
this (Makefile on macOS/Linux, bootstrap.ps1 on Windows); everything after is
identical on every OS, so it lives here instead of in three shell scripts.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
import labkit  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent


def step(title: str, script: str, *args: str) -> None:
    labkit.banner(title)
    rc = subprocess.run([sys.executable, str(HERE / script), *args], check=False).returncode
    if rc != 0:
        labkit.die(f"{script} failed (exit {rc}).", "Fix the error above and re-run: make setup")


def main() -> int:
    step("1/3  Probing hardware", "detect-hardware.py")

    hw = labkit.load_hardware()
    if not hw["recommendation"]["ram_sufficient"]:
        print(f"\n  !! {hw['ram_gb']} GB RAM < {labkit.MIN_RAM_GB} GB floor.")
        print("     Setup will continue, but expect swapping. The supported path for")
        print("     this machine is cloud/Day20-lab.ipynb (Colab / Kaggle).")

    step("2/3  Fetching the llama.cpp runtime", "fetch-runtime.py")
    step("3/3  Downloading Gemma 4 E2B (two quantizations, ~5.6 GB)", "download-model.py")

    labkit.banner("Setup complete")
    print("  Next:")
    print("    make bench      # track 01 - TTFT / TPOT / percentiles, both quants")
    print("    make tune       # track 01 - find your best thread count (before/after)")
    print("    make serve      # track 02 - OpenAI-compatible server + /metrics on :8080")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
