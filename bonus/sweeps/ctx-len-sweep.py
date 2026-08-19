#!/usr/bin/env python3
"""BONUS - Context-length sweep: watch TTFT grow super-linearly.

Attention is O(N^2) in sequence length, so doubling the prompt more than doubles
prefill time. That curve *is* TTFT in long-context RAG, and it is the reason the
deck's disaggregated prefill/decode pattern exists at all: prefill is
compute-bound and will happily starve every decode sharing the device.

Grid is capped by your RAM, since each point also allocates KV cache.

    make sweep-ctx
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
import labkit  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Prefill cost vs context length (bonus).")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--grid", default="", help="Comma-separated prompt lengths, e.g. 128,512,2048")
    args = ap.parse_args()

    hw = labkit.load_hardware()
    model = str(labkit.repo_root() / labkit.load_active()["primary_model"])
    ram = hw.get("ram_gb", 8)

    if args.grid:
        grid = [int(x) for x in args.grid.split(",") if x.strip()]
    elif ram < 12:
        grid = [128, 256, 512, 1024, 2048]
    elif ram < 24:
        grid = [128, 256, 512, 1024, 2048, 4096]
    else:
        grid = [128, 256, 512, 1024, 2048, 4096, 8192]

    labkit.banner(f"Context-length sweep on {pathlib.Path(model).name}")
    print(f"  RAM {ram} GB -> grid {grid}")
    print(f"  ctx-size must cover the largest point: {max(grid)}\n")

    out = labkit.run_bench([
        "-m", model, "-t", str(labkit.threads(hw)), "-ngl", str(labkit.n_gpu_layers(hw)),
        "-p", ",".join(str(g) for g in grid), "-n", "0", "-r", str(args.reps),
    ])
    points = labkit.bench_all_pp(out)
    if not points:
        labkit.die("Could not parse llama-bench output.",
                   "Run it by hand to see what happened:",
                   f"  {labkit.runtime_bin('llama-bench')} -m {model} -p 128 -n 0")

    rows = []
    first = points[0]
    for tokens, tps in points:
        prefill_ms = (tokens / tps * 1000.0) if tps else 0.0
        # Perfectly linear scaling would keep tok/s flat; the ratio shows the penalty.
        linear_ms = (first[0] / first[1] * 1000.0) * (tokens / first[0]) if first[1] else 0.0
        rows.append({
            "tokens": tokens, "pp_tok_s": round(tps, 1),
            "prefill_ms": round(prefill_ms, 1),
            "vs_linear": round(prefill_ms / linear_ms, 2) if linear_ms else 0.0,
        })
        print(f"   {tokens:6d} tok   {tps:8.1f} tok/s   prefill {prefill_ms:8.1f} ms   "
              f"{rows[-1]['vs_linear']:.2f}x linear")

    table = labkit.md_table(
        ["Prompt tokens", "Prefill (tok/s)", "TTFT contribution (ms)", "vs linear scaling"],
        [[r["tokens"], f"{r['pp_tok_s']:.1f}", f"{r['prefill_ms']:.1f}", f"{r['vs_linear']:.2f}x"]
         for r in rows],
    )
    worst = rows[-1]
    md = f"""# Bonus - Context-length sweep (prefill cost)

Host `{labkit.host_tag()}` · llama.cpp `{labkit.LLAMA_CPP_BUILD}` ·
`threads={labkit.threads(hw)}` `ngl={labkit.n_gpu_layers(hw)}` · RAM {ram} GB

{table}

At {worst['tokens']} tokens, prefill alone costs **{worst['prefill_ms']:.0f} ms** --
{worst['vs_linear']:.2f}x what linear scaling from the smallest point would predict.
Every millisecond of that lands in TTFT before the user sees a single token.

This is the number to remember when someone proposes stuffing more retrieved
context into a RAG prompt "since the context window allows it".

## Your finding (required -- replace this line)

_At what prompt length does prefill start dominating your end-to-end latency?
Given that number, how many retrieved chunks can your RAG pipeline afford?_
"""
    out_path = labkit.write_report("bonus-ctx-len-sweep.md", md, rows)
    print("\n" + md)
    print(f"==> Wrote {out_path.relative_to(labkit.repo_root())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
