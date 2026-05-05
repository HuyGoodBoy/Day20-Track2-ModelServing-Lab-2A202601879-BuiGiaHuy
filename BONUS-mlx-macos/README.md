# BONUS — MLX on macOS (Apple Silicon)

Optional 30-minute side-quest: compare llama.cpp's Metal backend against **MLX**, Apple's array framework. MLX uses unified memory more aggressively than Metal-via-Metal-Performance-Shaders and sometimes wins on Apple Silicon by 1.3–2×.

> **Skip this** if you're not on an Apple Silicon Mac (M1, M2, M3, M4). MLX requires `arm64` macOS.

## Install

```bash
# from repo root, .venv activated
pip install mlx mlx-lm
```

That's it — no native build. `mlx-lm` ships precompiled wrappers and downloads MLX-format models on demand.

## Run a side-by-side

```bash
python BONUS-mlx-macos/compare-mlx-vs-llama-cpp.py
```

Behind the scenes:

1. Loads `models/active.json` to know which model tier you're on.
2. Maps it to the matching MLX-format model on Hugging Face (`mlx-community/<...>`).
3. Runs the same 10 prompts through both runtimes.
4. Writes `benchmarks/bonus-mlx-vs-llama-cpp.md`.

## What you'll likely see

| Apple Silicon | MLX vs llama.cpp Metal |
|---|---|
| M1 / M1 Pro | MLX 1.2–1.5× faster on decode |
| M2 / M3 | roughly even, MLX edges ahead at long context |
| M4 / M4 Pro / Max | MLX 1.3–1.8× faster on decode |

Why the variability: llama.cpp's Metal kernels are well-optimized but generic; MLX has Apple-specific kernel paths and benefits from unified-memory zero-copy more directly. Both are reasonable production choices on Apple Silicon — MLX wins on Apple, llama.cpp wins everywhere else (cross-platform).

## Optional: stretch reading

- **Core ML** — Apple's ML framework, not really designed for autoregressive LLMs, but Apple's [LLM-on-iOS demo](https://github.com/apple/ml-stable-diffusion) shows the path
- **MLC LLM** — TVM-based runtime that compiles models to Metal/Vulkan/CUDA. Slower to set up than MLX but more cross-platform
- **ExecuTorch** — Meta's mobile inference runtime; useful for true-mobile (iPhone/Android)

These are mentioned for context only — picking a stretch project for them is C-tier challenge territory in the main bonus track.
