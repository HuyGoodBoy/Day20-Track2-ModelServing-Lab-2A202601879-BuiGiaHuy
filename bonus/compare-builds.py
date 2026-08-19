#!/usr/bin/env python3
"""BONUS B1 - Does compiling it yourself actually beat the prebuilt binary?

The prebuilt release you have been using all lab is compiled for a generic
baseline CPU, because it has to run on every machine that downloads it. Your
source build with -DGGML_NATIVE=ON is compiled for *your* CPU specifically, and
can use whatever vector extensions it actually has (AVX2, AVX-512, NEON).

This runs the same llama-bench workload through both binaries and reports the gap.
On CPU-only laptops the gap is usually the largest single win available in this
lab -- which is why the bonus track favours weaker hardware.

    make build-llama      # clone + compile (5-15 min)
    make compare-builds
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import labkit  # noqa: E402


def prebuilt_bench() -> pathlib.Path | None:
    """llama-bench from runtime/ only, ignoring the source build."""
    exe = "llama-bench.exe" if sys.platform == "win32" else "llama-bench"
    root = labkit.runtime_dir()
    if not root.exists():
        return None
    for cand in sorted(root.rglob(exe)):
        if cand.is_file():
            return cand
    return None


def run(bench: pathlib.Path, model: str, threads: int, ngl: int, metric: str, reps: int) -> float:
    is_prefill = metric.startswith("pp")
    shape = ["-p", metric[2:], "-n", "0"] if is_prefill else ["-p", "0", "-n", "128"]
    proc = subprocess.run(
        [str(bench), "-m", model, "-t", str(threads), "-ngl", str(ngl), *shape, "-r", str(reps)],
        capture_output=True, text=True, check=False, timeout=1800,
    )
    return labkit.bench_metric(proc.stdout + proc.stderr, metric)


def version_of(binary: pathlib.Path) -> str:
    proc = subprocess.run([str(binary), "--version"], capture_output=True, text=True, check=False)
    text = (proc.stdout + proc.stderr).strip().splitlines()
    return text[0] if text else "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description="Prebuilt vs source-built llama.cpp (bonus B1).")
    ap.add_argument("--metric", default="tg128", help="tg128 = decode, pp512 = prefill")
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()

    pre = prebuilt_bench()
    src = labkit.source_build_bin("llama-bench")
    if not pre:
        labkit.die("No prebuilt llama-bench in runtime/.", "Run: make setup")
    if not src:
        labkit.die(
            "No source build found at bonus/llama.cpp/.",
            "Build it first: make build-llama",
        )

    hw = labkit.load_hardware()
    model = str(labkit.repo_root() / labkit.load_active()["primary_model"])
    threads, ngl = labkit.threads(hw), labkit.n_gpu_layers(hw)
    cpu = hw.get("cpu", {})
    exts = [n for n, k in (("AVX-512", "avx512"), ("AVX2", "avx2"), ("NEON", "neon"))
            if cpu.get(k)]

    labkit.banner(f"Prebuilt vs source build ({args.metric})")
    print(f"  model   : {pathlib.Path(model).name}")
    print(f"  threads : {threads}   ngl: {ngl}")
    print(f"  CPU     : {cpu.get('model', '?')}  [{', '.join(exts) or 'no vector extensions detected'}]")
    print(f"\n  prebuilt: {pre.relative_to(labkit.repo_root())}")
    print(f"            {version_of(pre)}")
    print(f"  source  : {src.relative_to(labkit.repo_root())}")
    print(f"            {version_of(src)}\n")

    print("  running prebuilt ...", flush=True)
    a = run(pre, model, threads, ngl, args.metric, args.reps)
    print(f"    {a:.1f} tok/s")
    print("  running source build ...", flush=True)
    b = run(src, model, threads, ngl, args.metric, args.reps)
    print(f"    {b:.1f} tok/s")

    if not a or not b:
        labkit.die("One of the binaries produced no number -- run each by hand to see why.")

    gain = b / a
    verdict = (
        f"the source build is **{gain:.2f}x faster**" if gain > 1.03 else
        f"the prebuilt binary is **{1 / gain:.2f}x faster**" if gain < 0.97 else
        "**they are within 3% -- no meaningful difference**"
    )

    table = labkit.md_table(
        ["Binary", "Built for", f"{args.metric} (tok/s)", "Relative"],
        [["prebuilt release", "generic baseline CPU", f"{a:.1f}", "1.00x"],
         ["your source build", f"this CPU (`-DGGML_NATIVE=ON`)", f"{b:.1f}", f"{gain:.2f}x"]],
    )
    md = f"""# Bonus B1 - Prebuilt vs source build

Host `{labkit.host_tag()}` · CPU `{cpu.get('model', '?')}`
Vector extensions detected: {', '.join(exts) or 'none'}
llama.cpp `{labkit.LLAMA_CPP_BUILD}` both sides · `threads={threads}` `ngl={ngl}` ·
metric `{args.metric}`, {args.reps} repetitions

{table}

On this machine, {verdict}.

before: {a:.1f} tok/s (prebuilt, generic baseline)
after:  {b:.1f} tok/s (source build, -DGGML_NATIVE=ON)
speedup: {gain:.2f}x

Same source revision, same model, same flags at runtime -- the only difference is
what the compiler was allowed to assume about the CPU.
{"A gap this small usually means the prebuilt binary already dispatches to the right kernels at runtime, or that this workload is bandwidth-bound rather than instruction-bound." if 0.97 <= gain <= 1.03 else ""}

## Your explanation (required -- replace this line)

_Why did the gap come out this size on your CPU? Tie it to something concrete --
which extensions your CPU has, and whether this workload is limited by
instructions or by memory bandwidth. If the prebuilt binary won, explain how that
is possible._
"""
    out = labkit.write_report(f"bonus-build-compare-{args.metric}.md", md,
                              {"prebuilt_tok_s": a, "source_tok_s": b, "speedup": round(gain, 3)})
    print("\n" + md)
    print(f"==> Wrote {out.relative_to(labkit.repo_root())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
