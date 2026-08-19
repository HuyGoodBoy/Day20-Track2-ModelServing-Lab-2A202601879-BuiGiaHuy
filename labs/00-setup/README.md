# 00 — Setup

Three steps, no compiler: probe your machine, fetch the llama.cpp binaries, download
the model.

```bash
make setup      # macOS / Linux — creates .venv, installs deps, then runs all three
```

Windows:

```powershell
pwsh -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1
```

## What each step does

| Script | Output | Notes |
|---|---|---|
| `detect-hardware.py` | `hardware.json` | Stdlib only — runs before any install. Every other track reads this for thread count and GPU offload defaults. |
| `fetch-runtime.py` | `runtime/b10488/…` | Asks the llama.cpp release API which assets exist, picks the right one for your OS + accelerator, extracts it. 10–35 MB (more for CUDA). |
| `download-model.py` | `models/*.gguf` + `models/active.json` | Gemma 4 E2B, two quantizations, ~5.2 GB total. |

Only `hardware.json` and `models/active.json` get committed. The weights and binaries
are gitignored, and `make verify` never asks for them.

## Outputs you commit

- **`hardware.json`** — rubric item 1
- **`models/active.json`** — rubric item 2

## Overrides

```bash
python labs/00-setup/fetch-runtime.py --list                 # all release assets
python labs/00-setup/fetch-runtime.py --asset <name> --force # pick one by hand
python labs/00-setup/download-model.py --with-mtp            # + MTP head (bonus C1)
python labs/00-setup/download-model.py --skip-download       # manifest only
```

Runtime knobs live in `.env.example` (`LAB_N_THREADS`, `LAB_N_CTX`, `LAB_PARALLEL`, …).
Copy it to `.env` only if you want to override the auto-detected values — the scripts
read the environment directly, so `LAB_N_THREADS=6 make bench` works too.

## If something fails

| Symptom | Fix |
|---|---|
| `unknown model architecture: 'gemma4'` | Your llama.cpp is too old. `make runtime` re-fetches the pinned build. This is why the lab does not use `llama-cpp-python`. |
| Hugging Face unreachable | [`MANUAL-DOWNLOAD.md`](MANUAL-DOWNLOAD.md) — browser download, then `--skip-download`. |
| GitHub API rate-limited | Harmless: the script falls back to a built-in asset name table. |
| `No prebuilt asset matches …` | Run with `--list`, pick manually with `--asset`, or build from source (`make build-llama`). |
| Under 8 GB RAM | [`cloud/`](../../cloud/README.md) — Colab or Kaggle, same artifacts, same grade. |

## Next

```bash
make bench
```

Step-by-step walkthrough for the whole lab: [`GUIDE.md`](../../GUIDE.md)
